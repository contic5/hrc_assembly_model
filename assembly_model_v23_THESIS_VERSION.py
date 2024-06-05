import random
import math
import copy
import time

def createarray(element,total):
    arr=[]
    for _ in range(total):
        arr.append(element)
    return arr
_sysrand = random.SystemRandom()
prioritynames=[]
prioritiesmaximum=createarray([],2)
prioritiesminimum=createarray([],2)
maximumattributevalues=createarray(-9999,0)
maximumattributeids=createarray(-1,0)
minimumattributevalues=createarray(9999,0)
minimumattributeids=createarray(-1,0)

averageattributevalues=createarray(-9999,0)

#Using files
usingfiles=True

#Show a lot of extra print outs
debug=False
displayattributes=False

#Extra features
calculateusingmax=False #If false, will calculate using average.
usingweightpenalty=True
humanselection=False #human selects the part to move
oneatatime=False #Only one arm moves at a time
randomposition=True #parts are in a random position.

#speed in cm per second.
humanspeed=30
robotspeed=20

#How much is a person slowed down by adding weight. weight is kg
slightlyencumbered=10
encumbered=15
veryencumbered=20


slightlyencumberedspeed=0.75
encumberedspeed=0.6
veryencumberedspeed=0.5



'''
slightlyencumberedspeed=0.66
encumberedspeed=0.5
veryencumberedspeed=0.33
'''

sizecutoff=50


#csk special features
autotargetheavy=False
autowaitheavy=False

autotargetbyid=False
humanids=[1,3,5,7]
robotids=[2,4,6]
curhumanids=copy.deepcopy(humanids)
currobotids=copy.deepcopy(robotids)

maxdis=120
totalmodels=5

priorityfileusing='pausemenu.csv'
class Item():
    x=0.0
    y=0.0
    z=0.0
    def __init__(self,x=0.0,y=0.0,z=0.0):
        self.x=x
        self.y=y
        self.z=z
        super().__init__()
    def __str__(self):
        return "x="+str(round(self.x,2))+" y="+str(round(self.y,2))+" z="+str(round(self.z,2))
    def distance(self,other): #Returns distance between two items
        if(isinstance(other,Item)): #Checks if Item is valid
            result=((self.x - other.x)**2 + (self.y - other.y)**2 + (self.z - other.z)**2)**0.5
            return result
        else:
            print("OTHER IS NOT AN ITEM")
            return None

class Part(Item):
    connectsto=[] #What part does this part connect to
    connectareas=[] #Areas on part x that other parts can connect to
    isbase=False
    weight=0.0
    length=0.0
    width=0.0
    height=0.0
    partid=0
    size=0
    stability=0
    connectdistance=0
    totalconnects=0 #The total number of connects a part has
    connectsfilled=0 #The number of connecting parts that have been placed in the connects for this part.
    def __init__(self,partid=0,label='',isbase=False,x=0,y=0,z=0,weight=0,length=0,width=0,height=0,danger=0,stability=0):
        self.partid=partid
        self.label=label
        self.isbase=isbase
        self.weight=weight
        self.length=length
        self.width=width
        self.height=height
        self.size=length*width*height
        self.danger=danger
        self.stability=stability
        self.connectareas=[]
        super().__init__(x,y,z)
    def addconnect(self,newconnect):
        self.totalconnects+=1
        self.connectareas.append(newconnect)
    def __str__(self):
        res='label:'+self.label+' id='+str(self.partid)+' '
        res+="x="+str(round(self.x,2))+" y="+str(round(self.y,2))+" z="+str(round(self.z,2))
        return res

#Connects are the holes where other parts are inserted
class Connect(Item):
    partid=0
    def __init__(self,part,partid,x=0.0,y=0.0,z=0.0):
        self.partid=partid
        truex=part.x+x
        truey=part.y+y
        truez=part.z+z
        super().__init__(truex,truey,truez)
    def __str__(self):
        return "id="+str(self.partid)+" x="+str(self.x)+" y="+str(self.y)+" z="+str(self.z)

class Arm(Item):
    global usingweightpenalty
    defaultmovementspeed=4.0
    movementspeed=defaultmovementspeed
    distancetraveled=0.0
    weightcarried=0.0
    curweightcarrying=0
    stabilitycarried=0
    stabilitycarrying=0
    dangercarrying=0
    dangercarried=0
    lockedon=False #Locked onto grabbing a part
    holdingpart=False  #Is this arm holding a part
    name=''
    xslope=0.0 #The xslope towards the next part or connect
    yslope=0.0 #The yslope towards the next part or connect
    zslope=0.0 #The zslope towards the next part or connect
    armid=0
    def __init__(self,x=0.0,y=0.0,z=0.0,movementspeed=4.0,armid=0,name=''):
        self.armid=armid
        self.name=name
        self.defaultmovementspeed=movementspeed
        self.movementspeed=movementspeed
        super().__init__(x,y,z)
    def calculateslope(self,item,pickup=False): #Calculate the right way to move toward a part
        distanceval=self.distance(item)
        if(distanceval==0):
            self.xslope=0
            self.yslope=0
            self.zslope=0
        else:
            self.xslope=(item.x-self.x)/distanceval
            self.yslope=(item.y-self.y)/distanceval
            self.zslope=(item.z-self.z)/distanceval
        '''
        if(self.holdingpart==True and self.name=='Human' and self.weightcarrying>=5):
            self.movementspeed=self.defaultmovementspeed/((self.weightcarrying-4)**0.5)
        '''
        if(usingweightpenalty):
            if(self.holdingpart==True and self.name=='Human' and self.weightcarrying>=veryencumbered):
                self.movementspeed=int(self.defaultmovementspeed*veryencumberedspeed)
            elif(self.holdingpart==True and self.name=='Human' and self.weightcarrying>=encumbered):
                self.movementspeed=int(self.defaultmovementspeed*encumberedspeed)
            elif(self.holdingpart==True and self.name=='Human' and self.weightcarrying>=slightlyencumbered):
                self.movementspeed=int(self.defaultmovementspeed*slightlyencumberedspeed)
                ##self.movementspeed=self.defaultmovementspeed/((self.weightcarrying)**0.66)
                if(debug):
                    print('Human weight effect: ','Weight=',self.weightcarrying,' movementspeed=',self.movementspeed,sep='')
        else:
            self.movementspeed=self.defaultmovementspeed
        '''
        self.xslope=(self.x-part.x)/distanceval
        self.yslope=(self.y-part.y)/distanceval
        self.zslope=(self.z-part.z)/distanceval
        '''

    def movetoitem(self,item):
        #Move towards items using slopes
        if(self.distance(item)<=5):
            self.distancetraveled+=self.distance(item)
            self.x=item.x
            self.y=item.y
            self.z=item.z
            #print(self.name,'reached item')
        else:
            self.x=self.movementspeed*self.xslope+self.x
            self.y=self.movementspeed*self.yslope+self.y
            self.z=self.movementspeed*self.zslope+self.z
            self.distancetraveled+=self.movementspeed
    def pickup(self,part):
        self.weightcarried+=part.weight
        self.stabilitycarried+=part.stability
        self.dangercarried+=part.danger

        self.weightcarrying=part.weight
        self.stabilitycarrying=part.stability
        self.dangercarrying=part.danger
        self.holdingpart=True
    def setpos(self,part):
        self.x=part.x
        self.y=part.y
        self.z=part.z

def rand(maxval):
    return _sysrand.randint(0,maxval)

def determinebestpart(currentpart,currentarm,selectedparts,parts):
    partscore=0
    bestpart=-1
    bestpartscore=-9999999999
    curattributeval=0.0
    global minimumattributevalues
    global maximumattributevalues
    global averageattributevalues
    global minimumattributeids
    global maximumattributeids
    global prioritiesmaximum
    global prioritiesminimum
    global prioritynames
    global priorityfileusing
    global curhumanids
    global currobotids

    usedauto=False
    if(currentarm.name=='Human' and debug):
        print('Human is determining best part')
    #Check parts other arm is holding
    '''
    for i in range(len(selectedparts)):
        if(arms[i]!=currentarm):
            if(selectedparts[i]!=None):
                print("When calculating best",currentarm.name,"part best",arms[i].name,"part is",selectedparts[i].partid)
            else:
                print("When calculating best",currentarm.name,"part best",arms[i].name,"part is None")
    '''
    #Calculating minimum and maximum attributes
    for j in range(len(parts)):
        for k in range(len(prioritynames)):
            if(prioritynames[k]=="Distance"):
                curattributeval=parts[j].connectdistance+currentarm.distance(parts[j])
            elif(prioritynames[k]=="Weight"):
                curattributeval=parts[j].weight
            elif(prioritynames[k]=="Stability"):
                curattributeval=parts[j].stability
            elif(prioritynames[k]=="Size"):
                curattributeval=parts[j].size
            elif(prioritynames[k]=="Danger"):
                curattributeval=parts[j].danger
                    
            if(curattributeval>maximumattributevalues[k]):
                maximumattributevalues[k]=curattributeval
                maximumattributeids[k]=j
            if(curattributeval<minimumattributevalues[k]):
                minimumattributevalues[k]=curattributeval
                minimumattributeids[k]=j
                
            averageattributevalues[k]=averageattributevalues[k]+curattributeval
            if(curattributeval>maximumattributevalues[k]):
                maximumattributevalues[k]=curattributeval
                maximumattributeids[k]=j
            if(curattributeval<minimumattributevalues[k]):
                minimumattributevalues[k]=curattributeval
                minimumattributeids[k]=j
                
    #Calculating score based on priorities for maximum and minimum attributes
    for j in range(len(parts)):
        partscore=0
        for k in range(len(prioritynames)):
            if(prioritynames[k]=="Distance"):
                curattributeval=parts[j].connectdistance+currentarm.distance(parts[j])
            elif(prioritynames[k]=="Weight"):
                curattributeval=parts[j].weight
                if(parts[j].size<sizecutoff and currentarm.name=='Robot'):
                    partscore-=1000
                if(parts[j].weight>=veryencumbered and currentarm.name=='Robot' and 'NOTCSK' in priorityfileusing and autotargetheavy):
                    partscore+=1000
                if(parts[j].weight>=veryencumbered and currentarm.name=='Human' and 'NOTCSK' in priorityfileusing and autowaitheavy):
                    partscore-=1000
            elif(prioritynames[k]=="Stability"):
                curattributeval=parts[j].stability
            elif(prioritynames[k]=="Size"):
                curattributeval=parts[j].size
            elif(prioritynames[k]=="Danger"):
                curattributeval=parts[j].danger

            #Calculate using max for each priority
            if(calculateusingmax):
                if(maximumattributevalues[k]==0):
                    partscore+=prioritiesmaximum[currentarm.armid][k]*1
                else:
                    partscore+=prioritiesmaximum[currentarm.armid][k]*(curattributeval/maximumattributevalues[k])
                if(curattributeval==0):
                    partscore+=(prioritiesminimum[currentarm.armid][k]*1)
                else:
                    partscore+=prioritiesminimum[currentarm.armid][k]*(minimumattributevalues[k]/curattributeval)
            #Calculate using average for each priority
            else:
                partscore+=prioritiesmaximum[currentarm.armid][k]*(curattributeval-averageattributevalues[k])
                partscore+=prioritiesminimum[currentarm.armid][k]*(averageattributevalues[k]-curattributeval)
                partscore/=1000
        
        if(len(curhumanids)>0 and parts[j].partid==curhumanids[0] and currentarm.name=='Human' and autotargetbyid and not usedauto):
            if(debug):
                print(parts[j].label+' targeted by human')
            curhumanids.remove(curhumanids[0])
            usedauto=True
            bestpartscore=100000
            bestpart=j
            break
        #print('Robot ID',currobotids[0],'Cur Part ID',parts[j].partid)
        if(len(currobotids)>0 and parts[j].partid==currobotids[0] and currentarm.name=='Robot' and autotargetbyid and not usedauto):
            if(debug):
                print(parts[j].label+' targeted by robot')
            currobotids.remove(currobotids[0])
            usedauto=True
            bestpartscore=100000
            bestpart=j
            break


        if(partscore>bestpartscore):
            bestpartscore=partscore
            bestpart=j
    
    if(currentarm.name=='Human' and debug):
        print('Best part for the human is',bestpart,'with bestpartscore',bestpartscore)
    if(bestpart!=-1):
        #print(currentarm.name,bestpartscore,parts[bestpart].label,parts[bestpart].weight)
        return parts[bestpart]
    else:
        return None
    

def getallvalidparts(currentpart,currentarm,selectedparts,parts):
    validparts=[]
    for j in range(len(parts)):
        alreadytargeted=False
        for k in range(len(selectedparts)): #Checking if part is already targeted
            if(parts[j]==selectedparts[k]):
                alreadytargeted=True
        if(parts[j].totalconnects==parts[j].connectsfilled and not alreadytargeted): #Checking if part has all of its connects filled
            validparts.append(parts[j])
    return validparts

def run(priorityfilename='None',currun=0):
    global minimumattributevalues
    global maximumattributevalues
    global averageattributevalues
    global minimumattributeids
    global maximumattributeids
    global prioritiesmaximum
    global prioritiesminimum
    global prioritynames
    global priorityfileusing
    global curhumanids
    global currobotids


    time=0 #How long it takes to finish task
    arms=[]

    
    '''
    xpos=[0,5,10,15,20,0,5,10,15,20,0,5,10,15,20,0,5,10,15,20,0,5]
    zpos=[10,15,20,0,5,10,15,20,0,5,10,15,20,0,5,10,15,20,0,5,10,15]
    '''
    xpos=[]
    zpos=[]
    for i in range(4):
        for j in range(4):
            xpos.append(i*maxdis//3)
            zpos.append(j*maxdis//3)
    humanarm=Arm(x=-10,y=0,z=-10,movementspeed=humanspeed,armid=0,name='Human')
    robotarm=Arm(x=-10,y=0,z=-10,movementspeed=robotspeed,armid=1,name='Robot')
    arms.append(humanarm)
    arms.append(robotarm)
    totalarms=len(arms)
    
    partsmoved=0
    parts=[]
    #handle priorities

    if(usingfiles):
        
        priorityfile=priorityfilename+".csv"
        f = open('priorities/'+priorityfile, "r")
        lineon=0
        started=False
        for x in f:
            x=x.rstrip('\n')
            if(started):
                if(x==''):
                    break
                arr=x.split(",")
                loc=int((lineon-1)/2)
                if(lineon>0):
                    arr=list(map(int, arr))
                if(lineon==0):
                    prioritynames=arr
                    if(debug):
                        print(prioritynames)
                elif(lineon%2==0):
                    if(debug):
                        print('min priorites for',arms[loc].name)
                        print(arr)
                    prioritiesminimum[loc]=arr
                elif(lineon%2==1):
                    if(debug):
                        print('max priorites for',arms[loc].name)
                        print(arr)
                    prioritiesmaximum[loc]=arr
                lineon+=1
            elif(x=='START'): #Allows for additional text to be inserted in file before START
                started=True
                #print("Start priorities")
    if(currun==0 and priorityfilename!='None'):
        print('priorities maximum',arms[0].name)
        print(prioritiesmaximum[0])
        print('priorities minimum 0',arms[0].name)
        print(prioritiesminimum[0])
        print('priorities maximum 1',arms[1].name)
        print(prioritiesmaximum[1])
        print('priorities minimum 1',arms[1].name)
        print(prioritiesminimum[1])
    modelid=(currun%totalmodels)+1
    modelid=6
    f = open("models/attributesv"+str(modelid)+".csv", "r")
    lineon=0
    started=False
    for x in f:
        x=x.rstrip('\n')
        arr=x.split(",")
        if(started):
            if(lineon>0):
                #print(lineon)
                if(len(arr)>1):
                    if(arr[2].upper()!='TRUE'):
                        arr[2]=False
                    else:
                        arr[2]=True
                    if(randomposition):
                        parts.append(Part(partid=int(arr[0]),label=arr[1],isbase=arr[2],x=rand(maxdis),
                        y=0,z=rand(maxdis),length=int(arr[3]),width=int(arr[4]),
                        height=int(arr[5]),weight=float(arr[6]),danger=int(arr[7]),stability=int(arr[8])))
                    else:
                        parts.append(Part(partid=int(arr[0]),label=arr[1],isbase=arr[2],x=xpos[lineon-1],
                        y=0,z=zpos[lineon-1],length=int(arr[3]),width=int(arr[4]),
                        height=int(arr[5]),weight=float(arr[6]),danger=int(arr[7]),stability=int(arr[8])))
                else:
                    lineon-=1
            lineon+=1
        elif(arr[0]=='START'): #Allows for additional text to be inserted in file before START
            started=True
            #print("Start parts")
    if(debug):
        print(len(parts))
    averageattributevalues=createarray(-9999,len(parts))
    maximumattributevalues=createarray(-9999,len(parts))
    maximumattributeids=createarray(-1,len(parts))
    minimumattributevalues=createarray(9999,len(parts))
    minimumattributeids=createarray(-1,len(parts))

    curhumanids=copy.deepcopy(humanids)
    curobotids=copy.deepcopy(robotids)
    
    f = open("models/connectsv"+str(modelid)+".csv", "r")
    lineon=0
    curid=-1
    started=False
    firstconnect=-1
    for x in f:
        x=x.rstrip('\n')
        if(started):
            arr=x.split(",")
            if(debug):
                print(arr)
            if(len(arr)==2):
                #print('Adding connects to part',parts[i].partid)
                curid=int(arr[1])
                if(firstconnect==-1):
                    firstconnect=curid
                    if(debug):
                        print('firstconnect=',curid)
            elif(len(arr)>1):
                #print('Next connect to add')
                parts[curid].addconnect(Connect(parts[curid],partid=int(arr[1]),x=int(arr[2]),y=int(arr[3]),z=int(arr[4])))
        elif(x=='START'): #Allows for additional text to be inserted in file before START
            started=True
            #print("Start connects")

    partsthatconnect=[]
    for i in range(len(parts)):
        for j in range(len(parts[i].connectareas)):
            if(not parts[i].connectareas[j].partid in partsthatconnect):
                partsthatconnect.append(parts[i].connectareas[j].partid)

    if(debug):
        print('Total connects',parts[4].totalconnects)
        print('Connects',parts[4].connectareas)
    connectpart=[]
    partscopy=[]
    
    for i in range(len(parts)): #Remove first connect and track parts that have connects
        part=parts[i]
        if(part.isbase==True):
            if(debug):
                print('Part',str(part.partid),'is base')
            connectpart.append(part)

            #Make sure not to add the first part that remains still
            if(part.partid!=firstconnect):
                partscopy.append(part)
            '''
            if(part.partid in partsthatconnect):
                partscopy.append(part)
            '''
                #print("Part",part.label,"will be the base")
                #print("Part",part.partid,"will be the base")
        else:
            partscopy.append(part)
    parts=partscopy

    if(debug):
        print(connectpart[0].partid)
        print(connectpart[0].connectareas)

    
    #print("The length of parts is",len(parts))
    #Determine how far parts are from their connects
    for i in range(len(parts)):
        for j in range(len(connectpart)):
            currentconnect=None
            for k in range(len(connectpart[j].connectareas)):
                if(parts[i].partid==connectpart[j].connectareas[k].partid):
                    currentconnect=connectpart[j].connectareas[k]
            if(currentconnect!=None):
                parts[j].connectdistance=parts[i].distance(currentconnect)
    totalconnects=0
    for j in range(len(connectpart)):
        totalconnects+=len(connectpart[j].connectareas)
    #print("The length of connects is",totalconnects)
    #print("The total number of parts with connects is",len(connectpart))
    '''
    for i in range(len(connectpart)):
        print("Part",connectpart[i].partid,'has',connectpart[i].totalconnects,'connects')
    '''
    selectedparts=createarray(None,totalarms)
    bestconnects=createarray(None,totalarms)
    currentconnectpart=createarray(None,totalarms)

    #Start grabbing parts
    if(debug):
        print("Running using",priorityfilename)
    
    if(debug):
        print(connectpart[0].partid)
        print(connectpart[0].connectareas)
        for i in range(len(parts)):
            print(parts[i])
    while(len(parts)>0):
        for i in range(totalarms):
            #print("Turn",i,arms[i].lockedon,arms[i])
            #Determine next part for robot
            validparts=getallvalidparts(selectedparts[i],arms[i],selectedparts,parts)
            otherarmslockedon=False
            for j in range(totalarms):
                if(selectedparts[j]!=None and i!=j):
                    otherarmslockedon=True
            '''
            if(i==1):
                print(selectedparts[0],selectedparts[1],not(otherarmslockedon),partsmoved%len(arms)==i,not(oneatatime))
            '''
            valid=((not otherarmslockedon and partsmoved%len(arms)==i) or not oneatatime)
            if(not arms[i].lockedon and valid):
                if(i==0 and humanselection):
                    bestpart=determinebestpart(selectedparts[i],arms[i],selectedparts,validparts)
                    if(len(validparts)>0):
                        print("Valid parts include:")
                        for j in range(len(validparts)):
                            print(validparts[j].partid,end=' ')
                        print("Best part is",bestpart.label)
                        print("CHECKING FOR HUMAN INPUT")
                        selectedpartid=-1
                        while(selectedpartid==-1):
                            selectedpartid=int(input("Select a part by id: "))
                        selectedparts[i]=validparts[0]
                        for j in range(len(parts)):
                            if(parts[j].partid==selectedpartid):
                                selectedparts[i]=parts[j]
                                break
                        print("Best",arms[i].name,"part is",selectedparts[i].partid)
                else:
                    selectedparts[i]=determinebestpart(selectedparts[i],arms[i],selectedparts,validparts)
                    if(arms[i]==0):
                        print('Human arm selected',arms[i].name,'',selectedparts[i])
                    if(selectedparts[i]!=None):
                        if(debug):
                            print(arms[i].name,'',selectedparts[i])

                if(selectedparts[i]!=None):
                    arms[i].calculateslope(selectedparts[i])
                    #print('Slope for',arms[i].name,arms[i],'to',selectedparts[i],'is x=',round(arms[i].xslope,2),'y=',round(arms[i].yslope,2),'z=',round(arms[i].zslope,2))
                    bestconnects[i]=None
                    #print("Best",arms[i].name,"part is",selectedparts[i].partid)
                    #Determine best connect
                    for j in range(len(connectpart)):
                        for k in range(len(connectpart[j].connectareas)):
                            if(selectedparts[i].partid==connectpart[j].connectareas[k].partid):
                                currentconnectpart[i]=connectpart[j]
                                bestconnects[i]=connectpart[j].connectareas[k]
                                if(debug):
                                    print("Best",arms[i].name,"connect is",bestconnects[i].partid)
                                break
                    if(bestconnects[i]==None):
                        print('WARNING bestconnects[',(i),'] is none',sep='')
                    arms[i].lockedon=True

            #Robot Movement
            if(selectedparts[i]!=None and bestconnects[i]!=None):
                #Not holding part
                if(not arms[i].holdingpart):
                    #print(arms[i].name,"position=",arms[i],"Partposition=",selectedparts[i],'distance=',arms[i].distance(selectedparts[i]))
                    if(arms[i].distance(selectedparts[i])<arms[i].movementspeed):
                        #print(arms[i].name,"is grabbing part",selectedparts[i].partid)
                        for j in range(len(connectpart)):
                            for k in range(len(connectpart[j].connectareas)):
                                if(connectpart[j].connectareas[k].partid==part.partid):
                                    part.connectsto.append(connectpart[j].partid)
                        arms[i].pickup(selectedparts[i])
                        arms[i].calculateslope(bestconnects[i])
                        #print('Slope for',arms[i].name,arms[i],'to',bestconnects[i],'is x=',round(arms[i].xslope,2),'y=',round(arms[i].yslope,2),'z=',round(arms[i].zslope,2))
                    if(not arms[i].holdingpart):
                        arms[i].movetoitem(selectedparts[i])
                #Holding part and moving to connect
                else:
                    #print("Robotposition=",robotarm,"ConnectPosition=",bestrobotconnect,'distance=',robotarm.distance(bestrobotconnect))
                    if(arms[i].distance(bestconnects[i])<arms[i].movementspeed):
                        #part has been moved
                        partsmoved+=1
                        #Remove part from list if it no longer needs to connect to anything
                        doneconnecting=True
                        for j in range(len(parts)):
                            for k in range(len(selectedparts[i].connectareas)):
                                if(selectedparts[i].connectareas[k].partid==parts[j].partid):
                                    print("NOT DONE WITH THIS PART YET")
                                    doneconnecting=False
                                    break
                            if(not doneconnecting):
                                break
                        for j in range(len(parts)):
                            if(parts[j].partid==bestconnects[i].partid):
                                parts[j].weight+=selectedparts[i].weight
                        if(doneconnecting):
                            parts.remove(selectedparts[i])
                        arms[i].holdingpart=False
                        arms[i].lockedon=False
                        currentconnectpart[i].connectsfilled+=1
                        #print(arms[i].name,"placed part",selectedparts[i].partid,". List now holds",len(parts),"parts.")
                        if(debug):
                            print(arms[i].name," placed part ",selectedparts[i].label,". List now holds ",len(parts)," parts.",sep='')
                        if(len(parts)>0):
                            if(len(parts)>1):
                                if(debug):
                                    print('The remaining parts to place are',end=' ')
                            else:
                                if(debug):
                                    print('The remaining part to place is',end=' ')
                            if(debug):
                                for j in range(len(parts)):
                                    if(j+1<len(parts)):
                                        print(parts[j].partid,',',sep='',end='')
                                    else:
                                        print(parts[j].partid)
                                print()
                        else:
                            if(debug):
                                print("All Done!")
                        selectedparts[i]=None
                    if(arms[i].lockedon):
                        arms[i].movetoitem(bestconnects[i])
            if(len(parts)==0):
                break
        time+=1
        if(time>300):
            print("TIME OUT")
            break
    if(debug):
        print("When done, parts remaining=",len(parts))
        print()
    if(displayattributes):
        print("Displaying results when using",priorityfilename)
        for i in range(len(arms)):
            print(arms[i].name," total distance traveled is",round(arms[i].distancetraveled,2))
            print(arms[i].name,"total weight carried is",round(arms[i].weightcarried,2))
            print(arms[i].name,"total stability value carried",round(arms[i].stabilitycarried,2))
            print(arms[i].name,"total danger value carried",round(arms[i].dangercarried,2))
        print("Total time is",time)
        print('----------------------------------------------------------')
    result=[arms[0].distancetraveled,arms[0].weightcarried,arms[0].stabilitycarried,arms[0].dangercarried,time]
    return result

def printpriorityset(priorityset):
    print(priorityset[0][0])
    print(priorityset[0][1])
    print(priorityset[1][0])
    print(priorityset[1][1])

def main():
    global prioritiesmaximum
    global prioritiesminimum
    global usingfiles
    totalruns=1000
    firstrun=True
    truestarttime=time.time()
    if(usingfiles):
        totalruns=1000
        #priorityfilenames=['prioritiescskoriginal','prioritiescsk','prioritiescskv2','prioritiescskv3','prioritiesblank','prioritiesclosest','prioritiesnorobot','prioritiesweight',
        #'bruteforcecskv6','bruteforcecskv7','bruteforcecskv8','bruteforcecskv9','bruteforcecskv10','bruteforcecskv11','bruteforcecskv12','bruteforcecskv13','bruteforcecskv14']
        priorityfilenames=['thesispriorities']
        priorityfilenames=['prioritiescskoriginal','prioritiescskv3','prioritiesblank','prioritiesclosest','prioritiesnorobot','work','workv3','thesispriorities']
        
        averagedistances=[]
        averageweights=[]
        averagestabilities=[]
        averagedangers=[]
        averagetimes=[]
        for priorityfilename in priorityfilenames:
            overalldistance=0
            overallweight=0
            overallstability=0
            overalldanger=0
            overalltime=0
            print('Running',priorityfilename)
            for i in range(totalruns):
                result=run(priorityfilename,i)
                overalldistance+=result[0]
                overallweight+=result[1]
                overallstability+=result[2]
                overalldanger+=result[3]
                overalltime+=result[4]
                firstrun=False
            averagedistance=overalldistance/totalruns
            averageweight=overallweight/totalruns
            averagestability=overallstability/totalruns
            averagedanger=overalldanger/totalruns
            averagetime=overalltime/totalruns

            averagedistances.append(averagedistance)
            averageweights.append(averageweight)
            averagestabilities.append(averagestability)
            averagedangers.append(averagedanger)
            averagetimes.append(averagetime)
            print('Finished running',priorityfilename)
            print()
        print()
        print('Results')
        for i in range(len(priorityfilenames)):
            print('average distance for',priorityfilenames[i],'is',round(averagedistances[i],1))
        print()
        for i in range(len(priorityfilenames)):
            print('average weight for',priorityfilenames[i],'is',round(averageweights[i],1))
        print()
        for i in range(len(priorityfilenames)):
            print('average stability for',priorityfilenames[i],'is',round(averagestabilities[i],1))
        print()
        for i in range(len(priorityfilenames)):
            print('average danger for',priorityfilenames[i],'is',round(averagedangers[i],1))
        print()
        for i in range(len(priorityfilenames)):
            print('average time for',priorityfilenames[i],'is',round(averagetimes[i],1))
    else:
        totalruns=100
        maxchange=500
        start=maxchange//2
        end=0
        change=maxchange//10
        #Distance,Weight,Danger,Stability,Size
        #Humans should handle less stable parts
        #Humans should handle less dangerous parts
        #Humans should handle parts that are closer
        #Humans should handle lighter parts
        prioritiesminimum[0]=[100,100,150,50,0]
        prioritiesmaximum[0]=[0,0,0,0,0]

        

        prioritiesmaximum[1]=[end,end,end,end,end]
        prioritiesminimum[1]=[start,start,start,start,start]
        # values priorities cannot go below
        robotlimits=[0,50,50,-150,-100]
        #Distance,Weight,Danger,Stability,Size
        #Robots should handle more stable parts
        #Robots should handle more dangerous parts
        #Robots should handle parts that are somewhat closer
        #Robots should handle heavier parts
        prioritynames=['Distance','Weight','Danger','Stability','Size']
        robotmin=[-2*change,1*change,4*change,1*change,0*change]
        robotmax=[2*change,4*change,6*change,2*change,0*change]

        maximumset=[]
        minimumset=[]
        prioritytimes=[]
        changes=[]
        vals=[0]*6
        for i in range(-start,start+1,change):
            changes.append(i)
        print(changes)
        lowesttime=100000
        lowestminimum=prioritiesminimum
        lowestmaximum=prioritiesmaximum
        #Distance,Weight,Danger,Stability,Size
        changelen=len(changes)
        totalcombos=len(changes)**5
        firstvalid=True

        for i in range(len(prioritynames)):
            print(prioritynames[i])
            for j in range(len(changes)):
                if(changes[j]>=robotmin[i] and changes[j]<=robotmax[i]):
                    print(changes[j],end=' ')
            print()
        '''
        for i in range(totalcombos*2+1):
            x=i-1
            if(i>0):
                vals[0]=changes[(x//(changelen**0))%changelen]
                vals[1]=changes[(x//(changelen**1))%changelen]
                vals[2]=changes[(x//(changelen**2))%changelen]
                vals[3]=changes[(x//(changelen**3))%changelen]
                vals[4]=changes[(x//(changelen**4))%changelen]
                vals[5]=x//(totalcombos)%4
                print(vals)
        exit()
        '''
        estimatedtime=0
        loc=0
        for i in range(totalcombos+1):
            starttime=time.time()
            overalldistance=0
            overallweight=0
            overallstability=0
            overalldanger=0
            overalltime=0
            if(i>0):
                x=i-1
                for j in range(5):
                    prioritiesmaximum[1][j]=0
                    prioritiesminimum[1][j]=0
                vals[0]=changes[(x//(changelen**0))%changelen]
                vals[1]=changes[(x//(changelen**1))%changelen]
                vals[2]=changes[(x//(changelen**2))%changelen]
                vals[3]=changes[(x//(changelen**3))%changelen]
                vals[4]=changes[(x//(changelen**4))%changelen]
                vals[5]=x//(totalcombos)%2
                for j in range(5):
                    if(vals[j]>=0):
                        prioritiesminimum[1][j]=vals[j]
                    else:
                        prioritiesmaximum[1][j]=-vals[j]
            validconfig=True
            for j in range(len(robotlimits)):
                if(vals[j]<robotmin[j]):
                    validconfig=False
                if(vals[j]>robotmax[j]):
                    validconfig=False
                if(vals[2]<vals[j]*1.5 and j!=2):
                    validconfig=False
            if(validconfig):
                for j in range(totalruns):
                    result=run(priorityfilename='None',currun=j)
                    overalldistance+=result[0]
                    overallweight+=result[1]
                    overallstability+=result[2]
                    overalldanger+=result[3]
                    overalltime+=result[4]
                averagedistance=overalldistance/totalruns
                averageweight=overallweight/totalruns
                averagestability=overallstability/totalruns
                averagedanger=overalldanger/totalruns
                averagetime=overalltime/totalruns
                if(averagetime<lowesttime):
                    lowesttime=averagetime
                    lowestminimum=copy.deepcopy(prioritiesminimum)
                    lowestmaximum=copy.deepcopy(prioritiesmaximum)
                    if(averagetime<35):
                        print('Lowest Time')
                        print(averagetime)
                        string_ints = [str(int) for int in lowestmaximum[0]]
                        print(','.join(string_ints))
                        string_ints = [str(int) for int in lowestminimum[0]]
                        print(','.join(string_ints))
                        string_ints = [str(int) for int in lowestmaximum[1]]
                        print(','.join(string_ints))
                        string_ints = [str(int) for int in lowestminimum[1]]
                        print(','.join(string_ints))
                        exit()
                    #print('overall time for',priorityfilename,'is',overalltime)
                nexmax=copy.deepcopy(prioritiesmaximum)
                maximumset.append(nexmax)
           
                newmin=copy.deepcopy(prioritiesminimum)
                minimumset.append(newmin)
                    
                prioritytimes.append(averagetime)

                #TRACK PROGRESS
                curtime=time.time()
                executiontime=math.floor(curtime-truestarttime)
                if(validconfig and firstvalid):
                    estimatedtime=math.floor((curtime-starttime)*totalcombos)
                    firstvalid=False
                percent=int((100)*(i/(totalcombos)))
                print(executiontime,'/',estimatedtime,' seconds',sep='')
                print(i,'/',totalcombos,sep='')
                print(str(percent)+'%')
                string_ints = [str(int) for int in maximumset[loc][0]]
                print(','.join(string_ints))
                string_ints = [str(int) for int in minimumset[loc][0]]
                print(','.join(string_ints))
                string_ints = [str(int) for int in maximumset[loc][1]]
                print(','.join(string_ints))
                string_ints = [str(int) for int in minimumset[loc][1]]
                print(','.join(string_ints))
                print(averagetime)
            else:
                overalldistance+=999999
                overallweight+=999999
                overallstability+=999999
                overalldanger+=999999
                overalltime+=999999
                loc-=1
            loc+=1
            
        '''
        print('CHECKING LIST')
        print(len(maximumset))
        for i in range(len(maximumset)):
            print(i)
            string_ints = [str(int) for int in maximumset[i][0]]
            print(','.join(string_ints))
            string_ints = [str(int) for int in minimumset[i][0]]
            print(','.join(string_ints))
            string_ints = [str(int) for int in maximumset[i][1]]
            print(','.join(string_ints))
            string_ints = [str(int) for int in minimumset[i][1]]
            print(','.join(string_ints))
        exit()
        '''
        print('START SORTING')
        for i in range(len(prioritytimes)):
            if(i%100==0):
                print(i)
            max_idx=i
            for j in range(i,len(prioritytimes)):
                if(prioritytimes[max_idx]<prioritytimes[j]):
                    max_idx=j
            tempmax=copy.deepcopy(maximumset[i])
            maximumset[i]=copy.deepcopy(maximumset[max_idx])
            maximumset[max_idx]=copy.deepcopy(tempmax)
                    
            tempmin=copy.deepcopy(minimumset[i])
            minimumset[i]=copy.deepcopy(minimumset[max_idx])
            minimumset[max_idx]=copy.deepcopy(tempmin)

            temptime=copy.copy(prioritytimes[i])
            prioritytimes[i]=copy.copy(prioritytimes[max_idx])
            prioritytimes[max_idx]=copy.copy(temptime)
        endtime=time.time()-truestarttime
        print('end time=',round(endtime))
        print('Top 10 best for',changes)
        for i in range(len(maximumset)-10,len(maximumset)):
            string_ints = [str(int) for int in maximumset[i][0]]
            print(','.join(string_ints))
            string_ints = [str(int) for int in minimumset[i][0]]
            print(','.join(string_ints))
            string_ints = [str(int) for int in maximumset[i][1]]
            print(','.join(string_ints))
            string_ints = [str(int) for int in minimumset[i][1]]
            print(','.join(string_ints))
            print(prioritytimes[i])
            print()
        
        print('Lowest Time')
        string_ints = [str(int) for int in lowestmaximum[0]]
        print(','.join(string_ints))
        string_ints = [str(int) for int in lowestminimum[0]]
        print(','.join(string_ints))
        string_ints = [str(int) for int in lowestmaximum[1]]
        print(','.join(string_ints))
        string_ints = [str(int) for int in lowestminimum[1]]
        print(','.join(string_ints))
        print(prioritytimes[i])
main()