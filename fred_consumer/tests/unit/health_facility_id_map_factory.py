from fred_consumer.models import HealthFacilityIdMap
import factory

class HealthFacilityIdMapFactory(factory.Factory):
    FACTORY_FOR = HealthFacilityIdMap

    uid = factory.Sequence(lambda n: 'nBDPw7Qhd7r' + str(n))
    url = 'http://ec2-54-242-108-118.compute-1.amazonaws.com/api-fred/v1/facilities/' + str(uid)
#    def create(self, uid, url):
