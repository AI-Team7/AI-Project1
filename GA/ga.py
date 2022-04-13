import math
import random
import cv2
import csv
import matplotlib.pyplot as plt
import pandas as pd

# TSP 도시 생성 클래스
class City:
    # 생성자
    def __init__(self, x=None, y=None):
        self.x = None
        self.y = None
        if x is not None:
            self.x = x
        else:
            self.x = int(random.random() * 200)
        if y is not None:
            self.y = y
        else:
            self.y = int(random.random() * 200)

    def getX(self):
        return self.x

    def getY(self):
        return self.y

    # 도시 사이 거리 계산
    def distanceTo(self, city):
        xDistance = abs(self.getX() - city.getX())
        yDistance = abs(self.getY() - city.getY())
        distance = math.sqrt((xDistance * xDistance) + (yDistance * yDistance))
        return distance

    # 도시 x, y좌표 리턴
    def __repr__(self):
        return str(self.getX()) + ", " + str(self.getY())


# 여행 매니저
class TourManager:
    # 도착 도시 리스트
    destinationCities = []

    # 도착할 도시(클래스) 추가
    def addCity(self, city):
        self.destinationCities.append(city)

    # 도착한 도시 중에 가져오기
    def getCity(self, index):
        return self.destinationCities[index]

    # 도시 수 가져오기
    def numberOfCities(self):
        return len(self.destinationCities)


# 여행 클래스(적합도 계산)
class Tour:
    def __init__(self, tourmanager, tour=None):
        self.tourmanager = tourmanager
        self.tour = []
        self.fitness = 0.0
        self.distance = 0
        if tour is not None:
            self.tour = tour
        else:
            for i in range(0, self.tourmanager.numberOfCities()):
                self.tour.append(None)

    # 여행 수 리턴
    def __len__(self):
        return len(self.tour)

    # 특정 여행 리턴
    def __getitem__(self, index):
        return self.tour[index]

    # 특정 여행 설정
    def __setitem__(self, key, value):
        self.tour[key] = value

    # 결과 리턴
    def __repr__(self):
        geneString = 'Start -> '
        for i in range(0, self.tourSize()):
            geneString += str(self.getCity(i)) + ' -> '
        geneString += 'End'
        return geneString

    # 이동할 도시 추가
    def generateIndividual(self):
        for cityIndex in range(0, self.tourmanager.numberOfCities()):
            self.setCity(cityIndex, self.tourmanager.getCity(cityIndex))
        random.shuffle(self.tour)
        for cityIndex in range(0, self.tourmanager.numberOfCities()):
            if self.getCity(cityIndex) == self.tourmanager.getCity(0):
                self.tour[0], self.tour[cityIndex] = self.tour[cityIndex], self.tour[0]

    def getCity(self, tourPosition):
        return self.tour[tourPosition]

    def getIndex(self, city):
        return self.tour.index(city)

    def getCount(self):
        count = 0
        for i in range(0, self.tourSize()):
            if self.getCity(i) == None:
                count += 1
        return count

    # TSP에서 이용할 도시 리스트 추가
    def setCity(self, tourPosition, city):
        self.tour[tourPosition] = city
        self.fitness = 0.0
        self.distance = 0

    # fitness(적합도) 계산 후 리턴
    def getFitness(self):
        if self.fitness == 0:
            self.fitness = 1 / float(self.getDistance())
        return self.fitness

    # 거리 계산
    def getDistance(self):
        if self.distance == 0:
            tourDistance = 0
            for cityIndex in range(0, self.tourSize()):
                fromCity = self.getCity(cityIndex)
                destinationCity = None
                if cityIndex + 1 < self.tourSize():
                    destinationCity = self.getCity(cityIndex + 1)
                else:
                    destinationCity = self.getCity(0)
                tourDistance += fromCity.distanceTo(destinationCity)
            self.distance = tourDistance
        return self.distance

    # 여행 크기
    def tourSize(self):
        return len(self.tour)

    # 특정 도시가 여행에 포함되어있는지 확인
    def containsCity(self, city):
        return city in self.tour


# 인구 클래스
class Population:
    def __init__(self, tourmanager, populationSize, initialise):
        self.tours = []
        self.elit = []
        self.isElit = 0
        for i in range(0, populationSize):
            self.tours.append(None)

        if initialise:
            for i in range(0, populationSize):
                newTour = Tour(tourmanager)
                newTour.generateIndividual()
                self.saveTour(i, newTour)

    # 여행을 리스트에 추가
    def __setitem__(self, key, value):
        self.tours[key] = value

    def __getitem__(self, index):
        return self.tours[index]

    # 여행을 리스트에 추가
    def saveTour(self, index, tour):
        self.tours[index] = tour

    def getTour(self, index):
        return self.tours[index]

    def setElit(self):
        self.elit = self.getFittest()
        self.isElit = 1

    # 가장 적합도가 높은 투어 가져오기
    def getFittest(self):
        fittest = self.tours[0]
        for i in range(0, self.populationSize()):
            if fittest.getFitness() <= self.getTour(i).getFitness():
                fittest = self.getTour(i)
        return fittest

    # 여행들 리스트 크기
    def populationSize(self):
        return len(self.tours)

    def getFitnessList(self):
        fitness_list = []
        for i in range(0, self.populationSize()):
            fitness_list.append(self.getTour(i).getFitness())
        return fitness_list


# 유전 알고리즘 클래스
class GA:
    def __init__(self, tourmanager, mutationRate=0.1, tournamentSize=30, elitism=True):
        self.tourmanager = tourmanager
        self.mutationRate = mutationRate
        self.tournamentSize = tournamentSize
        self.elitism = elitism

    # 인구 클래스 진화 과정
    def evolvePopulation(self, pop):
        newPopulation = Population(self.tourmanager, pop.populationSize(), False)
        elitismOffset = 0
        if self.elitism:
            newPopulation.saveTour(0, pop.getFittest())
            elitismOffset = 1

        for i in range(elitismOffset, newPopulation.populationSize()):
            parent1 = self.tournamentSelection(pop)
            parent2 = self.tournamentSelection(pop)
            child = self.orderCrossover(parent1, parent2)
            newPopulation.saveTour(i, child)

        for i in range(elitismOffset, newPopulation.populationSize()):
            self.swapMutate(newPopulation.getTour(i))

        return newPopulation

    # 크로스오버 순서교차
    def orderCrossover(self, parent1, parent2):
        child = Tour(self.tourmanager)

        startPos = int(random.randint(1, parent1.tourSize()-1))
        endPos = int(random.randint(startPos + 1, parent2.tourSize()))

        for i in range(0, child.tourSize()):
            if i >= startPos and i <= endPos:
                child.setCity(i, parent1.getCity(i))

        for i in range(endPos+1, child.tourSize()):
            for j in range(1, child.tourSize()):
                if not child.containsCity(parent2.getCity(j)):
                    child.setCity(i, parent2.getCity(j))
                    break
        for i in range(0, startPos):
            for j in range(1, child.tourSize()):
                if i == 0:
                    child.setCity(0, parent2.getCity(0))
                    break
                if not child.containsCity(parent2.getCity(j)):
                    child.setCity(i, parent2.getCity(j))
                    break
        #print(child)
        #print(child.getCity(99))
        return child

    def frontOrderCrossover(self, parent1, parent2):
        child = Tour(self.tourmanager)

        startPos = int(random.random() * parent1.tourSize())
        endPos = int(random.random() * parent1.tourSize())

        for i in range(0, child.tourSize()):
            if startPos < endPos and i > startPos and i < endPos:
                child.setCity(i, parent1.getCity(i))
            elif startPos > endPos:
                if not (i < startPos and i > endPos):
                    child.setCity(i, parent1.getCity(i))

        for i in range(0, parent2.tourSize()):
            if not child.containsCity(parent2.getCity(i)):
                for ii in range(0, child.tourSize()):
                    if child.getCity(ii) == None:
                        child.setCity(ii, parent2.getCity(i))
                        break
        #print(child)
        return child

    def PMXCrossover(self, parent1, parent2):
        child = Tour(self.tourmanager)

        startPos = random.randint(1, parent1.tourSize() - 2)
        endPos = random.randint(startPos + 1, parent2.tourSize() - 1)

        for i in range(0, child.tourSize()):
            if i >= startPos and i <= endPos:
                child.setCity(i, parent1.getCity(i))

        for i in range(0, child.tourSize()):
            if i < startPos or i > endPos:
                child.setCity(i, parent2.getCity(i))

        duplicate = True
        while duplicate:
            duplicate = False
            target = child[startPos:endPos+1]
            for i in range(0, startPos):
                if child[i] in target:
                    duplicate = True
                    for j in range(startPos, endPos+1):
                        if child.getCity(i) == child.getCity(j):
                            child.setCity(i, parent2.getCity(j))
                            break

            #target = child[:endPos+1]
            for i in range(endPos+1, parent2.tourSize()):
                if child[i] in target:
                    duplicate = True
                    for j in range(startPos, endPos+1):
                        if child.getCity(i) == child.getCity(j):
                            child.setCity(i, parent2.getCity(j))
                            break
            """
            for i in range(1, child.tourSize()):
                if i >= startPos and i <= endPos:
                    # if not child.containsCity(parent2.getCity(i)):
                    if child.getCity(i) in child[startPos:endPos]:
                        duplicate = True
                        for j in range(1, child.tourSize()):
                            if j < startPos or j > endPos:
                                if child.getCity(j) == child.getCity(i):
                                    child.setCity(j, parent2.getCity(i))
            """

        #print(child.tourSize())
        return child

    def cycleCrossover(self, parent1, parent2):
        child = Tour(self.tourmanager)
        ind = 0
        first, second = parent1, parent2

        while True:
            if child.getCount() == 0:
                break
            child[ind] = first[ind]
            ind = first.getIndex(second[ind])
            #print(ind)
            if child[ind] != None and child.getCount() != 0:
                first, second = second, first
                ind = child.getIndex(None)
        return child

    # 변이(도시 위치 서로 바꾸기)
    def swapMutate(self, tour):
        for tourPos1 in range(1, tour.tourSize()):
            if random.random() < self.mutationRate:
                tourPos2 = int(tour.tourSize() * random.uniform(0.05, 1))

                city1 = tour.getCity(tourPos1)
                city2 = tour.getCity(tourPos2)

                tour.setCity(tourPos2, city1)
                tour.setCity(tourPos1, city2)

    def inversionMutate(self, tour):
        startPos = random.randint(1, tour.tourSize() - 2)
        endPos = random.randint(startPos + 1, tour.tourSize() - 1)

        child = Tour(self.tourmanager)
        tmp = 0
        for i in range(startPos, endPos+1):
            for j in range(endPos - tmp, startPos-1, -1):
                child.setCity(i, tour.getCity(j))
                tmp += 1
                break

        for i in range(startPos, endPos+1):
            tour.setCity(i, child.getCity(i))

    # 토너먼트 셀렉션
    def tournamentSelection(self, pop):
        t = 0.6
        n = 3
        tournament = []
        for i in range(0, 2**n):
            tournament.append(random.randint(0, pop.populationSize()-1))

        for i in reversed(range(1, n+1)):
            for j in range(0, 2**(i-1)):
                randomId = random.random()
                if t > randomId:
                    if pop.getTour(2*j).getFitness() > pop.getTour(2*j+1).getFitness():
                        tournament[j] = tournament[2*j]
                    else:
                        tournament[j] = tournament[2*j+1]
                else:
                    if pop.getTour(2*j).getFitness() < pop.getTour(2*j+1).getFitness():
                        tournament[j] = tournament[2*j]
                    else:
                        tournament[j] = tournament[2*j+1]
        return pop.getTour(tournament[0])

        # 좀 이상한 토너먼트(좋음)
        # tournament = Population(self.tourmanager, self.tournamentSize, False)
        # for i in range(0, self.tournamentSize):
        #     randomId = int(random.random() * pop.populationSize())
        #     tournament.saveTour(i, pop.getTour(randomId))
        # fittest = tournament.getFittest()
        # return fittest

    def rankingSelecton(self, pop):
        highest_chrom_idx = self.getSortedFitnessIndex(pop)
        prob_list = [0.5, 0.2, 0.15, 0.1, 0.05]
        p = random.random()
        sum = 0
        for i in range(5):
            sum += prob_list[i]
            if sum >= p:
                idx = i
                break
        return pop.getTour(highest_chrom_idx[idx])

    def getSortedFitnessIndex(self, pop):
        fitness_list = pop.getFitnessList()
        sortedFitness = sorted(fitness_list)
        highest_list = []
        highest_tour_index = []
        for i in range(0, 5):
            highest_fitness = sortedFitness.pop()
            highest_tour_index.append(fitness_list.index(highest_fitness))
        return highest_tour_index

    def elitSelection(self, pop):
        if pop.isElit:
            pop.saveTour(int(random.random() * pop.populationSize()), pop.elit)
        pop.setElit()

        return pop.getTour(int(random.random() * pop.populationSize()))

    def rouletteSelection(self, pop):
        sum = 0
        for i in range(pop.populationSize()):
            sum += pop.getTour(i).getFitness()

        fitnessProb = []
        for i in range(pop.populationSize()):
            fitnessProb.append(pop.getTour(i).getFitness() / sum)

        fitnessSum = 0
        fitness_sumList = []
        for i in fitnessProb:
            fitnessSum += i
            fitness_sumList.append(fitnessSum)
        #print(fitness_sumList)

        rand = random.random()
        #print(rand)
        for i in range(pop.populationSize()):
            if rand <= fitness_sumList[i]:
                #print(pop.getTour(i))
                return pop.getTour(i)

        return None

# 파일 직접 실행시 실행
if __name__ == '__main__':
    f = open('TSP.csv', 'r')
    reader = csv.reader(f)

    n_cities = 1000
    population_size = 10
    n_generations = 100
    cityCoordinate = []
    city_x = []
    city_y = []

    #random.seed(100)

    for line in reader:
        line0 = float(line[0])
        line1 = float(line[1])
        city = [line0, line1]
        cityCoordinate.append(city)
        city_x.append(line0)
        city_y.append(line1)
        if len(cityCoordinate) == n_cities:
            break
    f.close()

    # Load the map
    #map_original = cv2.imread('map.jpg')

    # Setup cities and tour
    tourmanager = TourManager()

    # 도시 수 만큼 랜덤 좌표 설정
    for i in range(n_cities):
        #x = random.randint(200, 800)
        #y = random.randint(200, 800)

        # 도시를 여행 매니저 리스트에 추가
        #tourmanager.addCity(City(x=x, y=y))
        tourmanager.addCity(City(x=city_x[i], y=city_y[i]))
        # 각 도시 위치에 점으로 표시
        #cv2.circle(map_original, center=(x, y), radius=10, color=(0, 0, 255), thickness=-1, lineType=cv2.LINE_AA)
        #plt.scatter(x, y)
        plt.scatter(city_x[i], city_y[i])
        plt.axis([0, 100, 0, 100])


    # map을 이름으로 사진 보여주기
    #cv2.imshow('map', map_original)
    #cv2.waitKey(0)

    # Initialize population
    pop = Population(tourmanager, populationSize=population_size, initialise=True)
    print("Initial distance: " + str(pop.getFittest().getDistance()))

    # Evolve population
    ga = GA(tourmanager)

    for i in range(n_generations):
        # population에 대해 유전알고리즘 시행 후 다시 저장
        pop = ga.evolvePopulation(pop)

        # 가장 적합도가 높은 여행
        fittest = pop.getFittest()

        if i == n_generations - 1:
            for j in range(1, n_cities):
                plt.plot([fittest[j].x, fittest[j - 1].x], [fittest[j].y, fittest[j - 1].y], color="blue")
        print(pop.getFittest())
        print("Final distance: " + str(pop.getFittest().getDistance()))
        # 지도에 반영
        #map_result = map_original.copy()

        """
        # 라인 그리기, 적합도가 가장 높은 투어에서 도시 순서대로 라인 그리기
        for j in range(1, n_cities):
            cv2.line(
                map_result,
                pt1=(fittest[j - 1].x, fittest[j - 1].y),
                pt2=(fittest[j].x, fittest[j].y),
                color=(255, 0, 0),
                thickness=3,
                lineType=cv2.LINE_AA
            )

        cv2.putText(map_result, org=(10, 25), text='Generation: %d' % (i + 1), fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                    fontScale=0.7, color=0, thickness=1, lineType=cv2.LINE_AA)
        cv2.putText(map_result, org=(10, 50), text='Distance: %.2fkm' % fittest.getDistance(),
                    fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.7, color=0, thickness=1, lineType=cv2.LINE_AA)
        cv2.imshow('map', map_result)
        if cv2.waitKey(100) == ord('q'):
            break
        """


    # Print final results
    print("Finished")
    print("Final distance: " + str(pop.getFittest().getDistance()))
    print("Solution:")
    print(pop.getFittest())
    plt.show()

    #cv2.waitKey(0)