import math
import random
import cv2
import csv
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans
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
    def __init__(self):
        self.destinationCities = []

    # 도착할 도시(클래스) 추가
    def addCity(self, city):
        self.destinationCities.append(city)

    # 도착한 도시 중에 가져오기
    def getCity(self, index):
        return self.destinationCities[index]

    # 도시 수 가져오기
    def numberOfCities(self):
        return len(self.destinationCities)

class KClustering:
    def cluster(self, k, tourmanager):
        df = pd.read_csv('TSP.csv', names=['x', 'y'])
        data = df[['x', 'y']]

        scaler = MinMaxScaler()
        data_scale = scaler.fit_transform(data)
        # k = 4

        # 그룹 수, random_state 설정
        model = KMeans(n_clusters=k, random_state=10)

        # 정규화된 데이터에 학습
        model.fit(data_scale)

        # 클러스터링 결과 각 데이터가 몇 번째 그룹에 속하는지 저장
        df["cluster"] = model.fit_predict(data_scale)

        for i in range(k):
            plt.scatter(df.loc[df['cluster'] == i, 'x'], df.loc[df['cluster'] == i, 'y'],
                        label='cluster' + str(i), s=10)
        plt.xlabel('X', size=12)
        plt.ylabel('Y', size=12)
        #plt.show()

        cities_of_cluster = []
        idxs_list = []
        for i in range(0, k):
            tmp = [cities for cities in df[df['cluster'] == i].index]
            idxs_list.append(tmp)
            tmp_list = []
            for k in tmp:
                tmp_list.append(tourmanager.getCity(k))
            cities_of_cluster.append(tmp_list)

        return cities_of_cluster, idxs_list

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

    # 가장 적합도가 높은 투어 가져오기
    def getFittest(self):
        fittest = self.tours[0]
        for i in range(0, self.populationSize()):
            if fittest.getFitness() <= self.getTour(i).getFitness():
                fittest = self.getTour(i)
        #print(len(fittest))
        return fittest

    # 여행들 리스트 크기
    def populationSize(self):
        return len(self.tours)


# 유전 알고리즘 클래스
class GA:
    def __init__(self, tourmanager, mutationRate=0.05, tournamentSize=5, elitism=True):
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
            child = self.crossover(parent1, parent2)
            newPopulation.saveTour(i, child)

        for i in range(elitismOffset, newPopulation.populationSize()):
            self.mutate(newPopulation.getTour(i))

        return newPopulation

    def crossover(self, parent1, parent2):
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
        return child

    # 변이(도시 위치 서로 바꾸기 SWAP)
    def mutate(self, tour):
        for tourPos1 in range(1, tour.tourSize()):
            if random.random() < self.mutationRate:
                tourPos2 = int(tour.tourSize() * random.uniform(0.05, 1))

                city1 = tour.getCity(tourPos1)
                city2 = tour.getCity(tourPos2)

                tour.setCity(tourPos2, city1)
                tour.setCity(tourPos1, city2)

    # 토너먼트 셀렉션
    def tournamentSelection(self, pop):
        tournament = Population(self.tourmanager, self.tournamentSize, False)
        for i in range(0, self.tournamentSize):
            randomId = int(random.random() * pop.populationSize())
            tournament.saveTour(i, pop.getTour(randomId))
        fittest = tournament.getFittest()
        return fittest

# 파일 직접 실행시 실행
if __name__ == '__main__':
    f = open('TSP.csv', 'r')
    reader = csv.reader(f)
    n_cities = 1000

    n_generations = 10
    cityCoordinate = []
    city_x = []
    city_y = []

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

    tourmanager = TourManager()
    for i in range(n_cities):
        tourmanager.addCity(City(x=city_x[i], y=city_y[i]))

    clustering = KClustering()
    k = 70
    cluster_cities, idx_list = clustering.cluster(k, tourmanager)

    population_size = []
    for i in range(0, k):
        population_size.append(len(cluster_cities[i]))
    print(population_size)

    # random.seed(100)

    # Load the map
    # map_original = cv2.imread('map.jpg')

    # Setup cities and tour
    tourmanagerList = []
    for i in range(0, k):
        tourmanagerList.append(TourManager())
    # 도시 수 만큼 랜덤 좌표 설정
    #for i in range(n_cities):
        # x = random.randint(200, 800)\
        # y = random.randint(200, 800)

        # 도시를 여행 매니저 리스트에 추가
        # tourmanager.addCity(City(x=x, y=y))
        # tourmanager.addCity(City(x=city_x[i], y=city_y[i]))
    for i in range(0, k):
        for city in cluster_cities[i]:
            tourmanagerList[i].addCity(city)
        #print(tourmanagerList[i].numberOfCities())


        # 각 도시 위치에 점으로 표시
        # cv2.circle(map_original, center=(x, y), radius=10, color=(0, 0, 255), thickness=-1, lineType=cv2.LINE_AA)
        # plt.scatter(x, y)

        # plt.scatter(city_x[i], city_y[i])
        # plt.axis([0, 100, 0, 100])

    # map을 이름으로 사진 보여주기
    # cv2.imshow('map', map_original)
    # cv2.waitKey(0)

    # Initialize population
    pop = []
    for i in range(0, k):
        pop.append(Population(tourmanagerList[i], populationSize=population_size[i], initialise=True))
        print("Initial distance: " + str(pop[i].getFittest().getDistance()))
        print(tourmanagerList[i].numberOfCities())

    # Evolve population
    ga = []
    for i in range(0, k):
        ga.append(GA(tourmanagerList[i]))

    colors = ["blue", "red", "green", "yellow", "blue", "red", "green", "yellow", "black", "grey"]
    for i in range(n_generations):
        for j in range(0, k):
        # population에 대해 유전알고리즘 시행 후 다시 저장
            pop[j] = ga[j].evolvePopulation(pop[j])

            # 가장 적합도가 높은 여행
            fittest = pop[j].getFittest()

            if i == n_generations - 1:
                for m in range(1, population_size[j]):
                    plt.plot([fittest[m].x, fittest[m - 1].x], [fittest[m].y, fittest[m - 1].y], linewidth="0.5")
    for i in range(0, k):
        print(pop[i].getFittest())
        print("Final distance: " + str(pop[i].getFittest().getDistance()))
        # 지도에 반영
        # map_result = map_original.copy()

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
    sum = 0
    for i in range(0, k):
        print("Final distance%d: %s" % (i+1, str(pop[i].getFittest().getDistance())))
        print("%d Solution:" % (i+1))
        print(pop[i].getFittest())
        print()
        sum += pop[i].getFittest().getDistance()
    print(sum)
    plt.show()

    # cv2.waitKey(0)