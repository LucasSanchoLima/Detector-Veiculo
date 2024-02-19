from pathlib import Path
import cv2
import os

################################
##Inicio - Comunicação Usuario##
################################

def EscolherVideo(caminhoVideos):
    Limpar()
    PrintBarras()
    print("Escolha um dos videos")
    PrintBarras()

    for x in range(len(caminhoVideos)):
        print(str(x+1) + " - " + str(caminhoVideos[x]))

    while 1:
        escolha = int(input("Numero: "))

        if escolha > 0 and escolha <= len(caminhoVideos):
            return caminhoVideos[escolha-1]
        
        print("Numero invalido, escolha um valido")

###########
#Auxilixar#
###########

def PrintBarras():
    print("====================================")

def Limpar():
    os.system('cls')

###############################
##Final - Comunicação Usuario##
###############################

#######################
##Inicio - Preparação##
#######################

def VerificacaoInicial():
    CriarDiretorio("./Videos/")
    CriarDiretorio("./Veiculos/")

    diretorioInicial = Path(".")
    caminhoVideos = list(diretorioInicial.glob("**/*.mp4"))
    caminhoVideos.extend(list(diretorioInicial.glob("**/*.avi")))

    if len(caminhoVideos) == 0:
        print("Nenhum video encontrado")
        exit()

    elif len(caminhoVideos) == 1:
        caminhoVideo = caminhoVideos[0]
    
    else: caminhoVideo = EscolherVideo(caminhoVideos)

    return FormatarCaminho(str(caminhoVideo))

###########
#Auxilixar#
###########

def CriarNomeArquivo(caminho):
    while caminho.find("/") != -1:
        caminho = caminho[caminho.find("/")+1::]
    return caminho[:caminho.find(".")]

def FormatarCaminho(caminho):
    return "./"+caminho.replace('\\', '/')

def CriarDiretorio(caminhoDiretorio):
    pathVideo = Path(caminhoDiretorio)
    if pathVideo.exists() == False:
        os.mkdir(caminhoDiretorio)

##############################
##Final - Preparação Inicial##
##############################

def RecarregarFrame(frame, corRetangulo=(0,0,0), corPonto=(0,0,0)):
    global recorteAX
    global posicao

    imagem = frame.copy()

    x = 0
    while x < len(recorteAx): 
        imagem = cv2.rectangle(imagem, recorteAx[x], recorteAx[x+1], corRetangulo, 1)
        x += 2

    imagem = Pintar(imagem, corPonto, posicao)

    cv2.imshow("Video", imagem)



def OrganizarRecorte(recorteAx):
    #formato: [xi, xf, yi, yf]
    recorte = []

    x = 0
    while x < len(recorteAx):
        if recorteAx[x][0] > recorteAx[x+1][0]:
            ax = recorteAx[x][0]
            recorteAx[x][0] = recorteAx[x+1][0]
            recorteAx[x+1][0] = ax

        if recorteAx[x][1] > recorteAx[x+1][1]:
            ax = recorteAx[x][1]
            recorteAx[x][1] = recorteAx[x+1][1]
            recorteAx[x+1][1] = ax

        recorte.append([recorteAx[x][0],recorteAx[x+1][0], recorteAx[x][1], recorteAx[x+1][1]])
        x += 2

    return recorte

def OrganizadorClick(pos):
    global posEscolha
    global posicao
    global recorteAx

    resultadoEscolha = posEscolha%3

    if resultadoEscolha == 0 or resultadoEscolha == 1:
        recorteAx.append(pos)
        posEscolha += 1
        if resultadoEscolha == 1:
            RecarregarFrame(frame, (0,255,0), (0,0,255))

    elif resultadoEscolha == 2:
        posicao.append(pos)
        posEscolha += 1
        RecarregarFrame(frame, (0,255,0), (0,0,255))

    #print(posEscolha, posicao, recorteAx, pos)

def Click(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        #print(str(frame[y][x]) + ": " + str(x) + ", " + str(y))
        OrganizadorClick([x,y])

def CriarQuadradoBusca(pos,tamanho):
    #formato: [[pixel1],[pixel2],[pixel3],[pixel4],[pixel5]]
    area = [pos]
    metade = int(tamanho/2)
    area.append([pos[0]-metade,pos[1]-metade])
    area.append([pos[0]+metade,pos[1]+metade])
    area.append([pos[0]+metade,pos[1]-metade])
    area.append([pos[0]-metade,pos[1]+metade])

    return area

def VerificarArea(area, frame, corBase, sensibilidade, diferente=1):
    x = 0
    contador = 0
    while x < len(area):
        if diferente:
            if frame[area[x][1]][area[x][0]][0] > corBase[0] + sensibilidade or frame[area[x][1]][area[x][0]][0] < corBase[0] - sensibilidade:
                contador+=1
        else:
            if frame[area[x][1]][area[x][0]][0] < corBase[0] + sensibilidade and frame[area[x][1]][area[x][0]][0] > corBase[0] - sensibilidade:
                contador+=1
        x+=1

    if contador == 5: return 1

    return 0

def Pintar(frame, cor, posicoes):
    for x in range(len(posicoes)):
        frame[posicoes[x][1]][posicoes[x][0]] = cor

    return frame

def PreparoUsuario(imagem):
    cv2.imshow("Video", imagem)
    #====================
    #Verificar se a tela do usuario é menor do que a frame do video
    #====================
    cv2.setMouseCallback("Video", Click)
    cv2.waitKey(0)

caminhoVideo = VerificacaoInicial()

print("Abrindo Video: " + caminhoVideo)

video = cv2.VideoCapture(caminhoVideo)

if video.isOpened() == False:
    print("Erro ao abrir o arquivo de video")
    exit()

retorno, frame = video.read()
original = frame.copy()

#input("Pressione enter para começar")

cor = [98, 61, 35]
sensibilidadeCarro = 15
sensibilidadePista = 8

tamanhoBusca = 16

posEscolha = 0
corAnterior = []
recorteAx = []
qtdCarro = []
qtdPixel = []
posicao = []
area = []
pista = []

PreparoUsuario(frame)

recorte = OrganizarRecorte(recorteAx)

for x in range(len(posicao)):
    pista.append(0)
    qtdCarro.append(0)
    qtdPixel.append(0)
    area.append(CriarQuadradoBusca(posicao[x], tamanhoBusca))
    corAnterior.append(cor)

caminhoSalvarCarro = "./Veiculos/"+CriarNomeArquivo(caminhoVideo)
CriarDiretorio(caminhoSalvarCarro)

for x in range(len(area)):
    CriarDiretorio(caminhoSalvarCarro+"/Area"+str(x+1))

if len(posicao) == 0:
    print("Nenhuma configuração escolhida")
    exit()

while video.isOpened():

    retorno, frame = video.read()

    if not retorno: break

    for x in range(len(posicao)):

        if VerificarArea(area[x], frame, corAnterior[x], sensibilidadeCarro) and pista[x]:
            pista[x] = 0
            qtdCarro[x] += 1
            cv2.imwrite(caminhoSalvarCarro+"/Area"+str(x+1)+"/Carro"+str(qtdCarro[x])+".jpg", Pintar(frame, (0,255,0), area[x])[recorte[x][2]:recorte[x][3],recorte[x][0]:recorte[x][1]])
                                                                                                                        
        elif VerificarArea(area[x], frame, corAnterior[x], sensibilidadePista, 0):
            pista[x] = 1
            #corAnterior[x] = frame[posicao[x][1]][posicao[x][0]]

    
print(qtdCarro)

cv2.destroyAllWindows()