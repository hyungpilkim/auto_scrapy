import json
import os
from collections import namedtuple
import copy
from define_data import DataGroup, DataJob
class FileManager():
    def __init__(self, file_nm):
        self.__file_path = "./" + file_nm
        #self.aes_manager = aes_util.AesUtil()
    
    def save_file(self, data_list):
        save_list = copy.deepcopy(data_list)

        '''
        for group in save_list:
            for job in group[DataGroup.attr_job_list]:
                if len(job[DataJob.attr_text_input]) > 0:
                    job[DataJob.attr_text_input] = self.aes_manager.encrypt(job[DataJob.attr_text_input])
        '''
        with open(self.__file_path, 'w') as outfile:
            json.dump(save_list, outfile, indent=4)

    def delete_file(self):
        if os.path.isfile(self.__file_path):
            os.remove(self.__file_path)
    
    def read_file(self):
        json_data = []        
        with open(self.__file_path, "r") as json_file:
            try:
                json_data = json.load(json_file)
            except json.decoder.JSONDecodeError as e:
                print(e.msg)

        for group in json_data:
            #grpup key 확인 / 추가
            for group_key in DataGroup.attr.keys():
                if group.get(group_key) == None:
                    group[group_key] = ""
                    
            for job in group[DataGroup.attr_job_list]:
                #job key 확인 / 추가
                for job_key in DataJob.attr.keys():
                    #print(job_key in job)
                    if job.get(job_key) == None:
                        job[job_key] = ""
                '''
                if len(job[DataJob.attr_text_input]) > 0:
                    job[DataJob.attr_text_input] = self.aes_manager.decrypt(job[DataJob.attr_text_input])
                '''
        return json_data
