import os
import sys
import pytest
import copy
from define_data import DataJob, DataGroup

print(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
import file_manager
import qt_gui
from collections import namedtuple
import aes_util
class TestClass():
    @pytest.fixture
    def file_manager(self):

        aes_manager = aes_util.AesUtil()

        self.group_list = []

        #초기데이터
        item_list1 = []

        job1 = copy.deepcopy(DataJob.attr)
        job1[DataJob.attr_idx] = '1'
        job1[DataJob.attr_is_check] = True
        job1[DataJob.attr_job_name] = 'test1'
        job1[DataJob.attr_url] = 'https://nid.naver.com/nidlogin.login?mode=form&url=https%3A%2F%2Fwww.naver.com'
        job1[DataJob.attr_text_selector] = ''
        job1[DataJob.attr_type_selector] = ''
        job1[DataJob.attr_type_action] = 'move'
        job1[DataJob.attr_text_input] = aes_manager.encrypt('test')
        job1[DataJob.attr_text_result] = ''

        item_list1.append(job1)

        job2 = copy.deepcopy(DataJob.attr)
        job2[DataJob.attr_idx] = '2'
        job2[DataJob.attr_is_check] = True
        job2[DataJob.attr_job_name] = 'test2'
        job2[DataJob.attr_url] = ''
        job2[DataJob.attr_text_selector] = '//*[@id="id"]'
        job2[DataJob.attr_type_selector] = '//*[@id="id"]'
        job2[DataJob.attr_type_action] = 'set'
        job2[DataJob.attr_text_input] = aes_manager.encrypt('aaa')
        job2[DataJob.attr_text_result] = ''
        
        item_list1.append(job2)

        job3 = copy.deepcopy(DataJob.attr)
        job3[DataJob.attr_idx] = '3'
        job3[DataJob.attr_is_check] = True
        job3[DataJob.attr_job_name] = 'test3'
        job3[DataJob.attr_url] = ''
        job3[DataJob.attr_text_selector] = '//*[@id="id"]'
        job3[DataJob.attr_type_selector] = '//*[@id="id"]'
        job3[DataJob.attr_type_action] = 'set'
        job3[DataJob.attr_text_input] = aes_manager.encrypt('aaa')
        job3[DataJob.attr_text_result] = ''
        item_list1.append(job3)

        item_list2 = []
        
        job4 = copy.deepcopy(DataJob.attr)
        job4[DataJob.attr_idx] = '4'
        job4[DataJob.attr_is_check] = True
        job4[DataJob.attr_job_name] = 'test4'
        job4[DataJob.attr_url] = ''
        job4[DataJob.attr_text_selector] = '//*[@id="id"]'
        job4[DataJob.attr_type_selector] = '//*[@id="id"]'
        job4[DataJob.attr_type_action] = 'set'
        job4[DataJob.attr_text_input] = aes_manager.encrypt('aaa')
        job4[DataJob.attr_text_result] = ''

        item_list2.append(job4)
        
        job5 = copy.deepcopy(DataJob.attr)
        job5[DataJob.attr_idx] = '5'
        job5[DataJob.attr_is_check] = True
        job5[DataJob.attr_job_name] = 'test5'
        job5[DataJob.attr_url] = ''
        job5[DataJob.attr_text_selector] = '//*[@id="id"]'
        job5[DataJob.attr_type_selector] = '//*[@id="id"]'
        job5[DataJob.attr_type_action] = 'set'
        job5[DataJob.attr_text_input] = aes_manager.encrypt('aaa')
        job5[DataJob.attr_text_result] = ''
        item_list2.append(job5)

        group1 = copy.deepcopy(DataGroup.attr)
        group1[DataGroup.attr_idx] = len(self.group_list);
        group1[DataGroup.attr_is_check] = True;
        group1[DataGroup.attr_text_name] = 'naver';
        group1[DataGroup.attr_num_reapeat] = 1;
        group1[DataGroup.attr_job_list] = item_list1;
        self.group_list.append(group1)

        group2 = copy.deepcopy(DataGroup.attr)
        group2[DataGroup.attr_idx] = len(self.group_list);
        group2[DataGroup.attr_is_check] = True;
        group2[DataGroup.attr_text_name] = 'test login';
        group2[DataGroup.attr_num_reapeat] = 1;
        group2[DataGroup.attr_job_list] = item_list2;
        self.group_list.append(group2)

        FileManager = file_manager.FileManager("test123")
        yield FileManager
        #FileManager.delete_file()
    
    def test_json(self, file_manager):  
        print(f'test_json')
        print(self.group_list)
        json = file_manager.save_file(self.group_list)
        read_list = file_manager.read_file()
        print('read_list', read_list)
        assert self.group_list == read_list
