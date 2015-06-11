
from ems.configuration.loader.base import Base
from ems.configuration.node import Node
import json as json

class Json(Base):

    def load(self, fileName, configObj):

        with open(fileName) as jsonFile:
            profiles = json.load(jsonFile)

        for idx, profile in enumerate(profiles):

            profileNode = Node()
            profileId = "profile-{0}".format(idx+1)

            for key in profile['data']:
                profileNode[key] = profile['data'][key]

            configObj.setProfileName(profileId, profile['name'])
            if profile["default"]:
                configObj.setDefaultProfile(profileId)

            configObj.setProfile(profileId, profileNode)

    def save(self, fileName, configObj):

        data = []

        for profileId in configObj.profiles:

            profile = configObj.getProfile(profileId)

            profileData = {
                'name' : configObj.getProfileName(profileId),
                'default': configObj.getDefaultProfileId() == profileId,
                'data': profile
            }

            data.append(profileData)

        with open(fileName, 'w') as outfile:
            json.dump(data, outfile, indent=4)