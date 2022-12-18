
from PyQt5 import QtWidgets, QtGui, QtCore
from multiprocessing import Queue
import sys
import copy
import file_manager
from define_data import DataGroup, DataJob, TypeSelector, TypeAction, TypeTarget
import pandas as pd
import conf
from datetime import datetime
'''
  tab1
  ----------------------------------------------------------------
  [browser open]  -- 1
  ----------------------------------------------------------------
  그룹리스트       -- 2
  번호 checkbox   이름       
  1.      V      그룹이름1   
  2.            그룹이름2   
  [그룹실행][삭제]
  ----------------------------------------------------------------
  세부항목         -- 3
  [group 이름][select add][저장] 
  번호   checkbox   lb_선택자      선택자구분    액션구분     리스트여부   결과값  
  1.      V      xpath1      xpath        click       N
  2.            testname1   class        gettext     Y
  3.
  4.
  [세부항목실행] [실행] [삭제]
'''


'''
작업 result
'''
class WorkerResultQ(QtCore.QThread):
    finished = QtCore.pyqtSignal(dict)
    def set_result_queue(self, result_q):
        self.result_q =  result_q
    def run(self):
        while True:
            if not self.result_q.empty():
                data = self.result_q.get()
                self.finished.emit(data)

file_nm = 'scrapy_info1'
class QtGui(QtWidgets.QMainWindow):
    def __init__(self, job_q, result_q):
        super(QtGui, self).__init__()
        self.g_job_q = job_q
        self.g_result_q = result_q
        
        self.worker = WorkerResultQ()
        self.worker.set_result_queue(self.g_result_q)
        self.worker.finished.connect(self.job_result)
        self.worker.start()

        self.init_ui()
        
    def init_ui(self):
        self.resize(1200, 800)
        self.center()
       
        self.file_manager = file_manager.FileManager(file_nm)
        self.load_data()
 
        self.layoutTop = LayoutTop()
        self.layoutGroup = LayoutGroup(self.group_list, self.cb_load_job, self.cb_run_group, self.cb_save, self.cb_clear_job)
        self.layoutJob = LayoutJob(self.cb_run_job)
        
        layout_top = self.layoutTop.create_layout()
        layout_middle = self.layoutGroup.create_layout()
        self.layoutGroup.bind_items()

        layout_bottom = self.layoutJob.create_layout()

        left_vbox_layout = QtWidgets.QVBoxLayout()
        right_vbox_layout = QtWidgets.QVBoxLayout()
        hbox_layout = QtWidgets.QHBoxLayout()
        
        #left_vbox_layout.addLayout(layout_top, 1)
        left_vbox_layout.addLayout(layout_middle, 2)
        left_vbox_layout.addLayout(layout_bottom, 3)
        
        self.result_edit = QtWidgets.QPlainTextEdit()
        self.result_table = QtWidgets.QTableWidget()
        self.btn_save_file = QtWidgets.QPushButton("테이블_파일저장")
        self.btn_save_file.clicked.connect(self.save_file)

        right_vbox_layout.addWidget(self.result_edit, 1)
        right_vbox_layout.addWidget(self.result_table, 2)
        right_vbox_layout.addWidget(self.btn_save_file, 1)

        hbox_layout.addLayout(left_vbox_layout, 2)
        hbox_layout.addLayout(right_vbox_layout)
        
        widget = QtWidgets.QWidget()
        widget.setLayout(hbox_layout)
        self.setCentralWidget(widget)
        
    @QtCore.pyqtSlot(dict)
    def job_result(self, data):
        
        if isinstance(data[DataJob.attr_text_result], list):
            result_data = data[DataJob.attr_text_result]
            print("list", data[DataJob.attr_text_result])
           
            self.result_table.setRowCount(len(result_data))
            self.result_table.setColumnCount(len(result_data[0]))       

            for rowIdx, item in enumerate(result_data):
                print("rowIdx", item)
                for colIdx, key in enumerate(item):
                    self.result_table.setItem(rowIdx, colIdx, QtWidgets.QTableWidgetItem(item[key])) 
           
        else:
            self.result_edit.appendPlainText(f'{data[DataJob.attr_job_name]} => {data[DataJob.attr_text_result]}')

    def center(self):
        qr = self.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    #job 바인딩
    def cb_load_job(self, row):
        self.layoutJob.set_item_list(self.group_list[row][DataGroup.attr_job_list])
        self.layoutJob.bind_items()

    #job 바인딩
    def cb_clear_job(self):
        self.layoutJob.set_item_list([])
        self.layoutJob.bind_items()

    #그룹 실행
    def cb_run_group(self, list):
        print('call cb_run_group',  list)
        self.g_job_q.put(list)

    #job 실행
    def cb_run_job(self, list):
        self.g_job_q.put(list)
    
    #파일 저장
    def cb_save(self):
        self.file_manager.save_file(self.group_list)

    #파일 로드
    def load_data(self):
        self.group_list = self.file_manager.read_file()
    
    #테이블 파일저장
    def save_file(self):
        tbl_rows = []
        for row in range(self.result_table.rowCount()):
            tbl_dict = {}
            for column in range(self.result_table.columnCount()):
                itm = self.result_table.item(row, column)
                tbl_dict[column] = itm.text()
            
            tbl_rows.append(tbl_dict)
        
        df = pd.DataFrame(tbl_rows)
        now = datetime.now()
        dt_string = now.strftime("%Y%m%d%H%M%S")
        df.to_csv(f"{conf.config['scrapy_file_path']}{dt_string}.csv", index=False, encoding="utf-8-sig")
        
#레이아웃 top 
class LayoutTop():
    def create_layout(self):
        result_layout = QtWidgets.QHBoxLayout()
        btn_open_browser = QtWidgets.QPushButton("Open 브라우저")
        result_layout.addWidget(btn_open_browser)
        return result_layout

#레이아웃 group 
class LayoutGroup():
    def __init__(self, group_list, cb_load_job, cb_run_group, cb_save, cb_clear_job) -> None:
        self.group_list = group_list
        self.table_widget = QtWidgets.QTableWidget()
        self.cb_load_job = cb_load_job
        self.cb_run_group = cb_run_group
        self.cb_save = cb_save
        self.cb_clear_job = cb_clear_job

    #레이아웃 생성
    def create_layout(self):
        '''
        그룹 리스트 | 행 추가
        rows
        전체선택 | 선택 실행 | 선택 삭제
        '''
        result_layout = QtWidgets.QVBoxLayout()
        label_title = QtWidgets.QLabel("그룹 리스트")
        result_layout.addWidget(label_title)

        #상단
        top_layout = QtWidgets.QHBoxLayout()
        btn_add = QtWidgets.QPushButton("행 추가")
        btn_svae = QtWidgets.QPushButton("파일 저장")

        top_layout.addStretch(1)
        top_layout.addWidget(btn_add)
        top_layout.addWidget(btn_svae)
        result_layout.addLayout(top_layout)

        self.table_widget.horizontalHeader().setSectionResizeMode(1)
        self.table_widget.setColumnCount(len(DataGroup.label_titles))
        self.table_widget.setHorizontalHeaderLabels(DataGroup.label_titles)

        self.table_widget.cellChanged.connect(self.ev_cell_change_text)
        result_layout.addWidget(self.table_widget)

        #하단
        bottom_layout = QtWidgets.QHBoxLayout()
        checkbox_all_select = QtWidgets.QCheckBox('전체선택')
        btn_run = QtWidgets.QPushButton("그룹 실행")
        btn_del = QtWidgets.QPushButton("그룹 삭제")
        bottom_layout.addWidget(checkbox_all_select)
        bottom_layout.addWidget(btn_run)
        bottom_layout.addWidget(btn_del)
        result_layout.addLayout(bottom_layout)

        btn_svae.clicked.connect(self.ev_save)
        btn_add.clicked.connect(self.ev_add_row)
        btn_run.clicked.connect(self.ev_run_group)
        btn_del.clicked.connect(self.ev_del_group)
        checkbox_all_select.stateChanged.connect(self.ev_changed_checkbox_all)
        self.table_widget.doubleClicked.connect(self.ev_cell_double_click)
        return result_layout
    
    #데이터 바인드
    def bind_items(self):
        self.table_widget.setRowCount(len(self.group_list))
        self.table_widget.setColumnCount(len(DataGroup.label_titles))       
 
        for rowIdx, item in enumerate(self.group_list):
            column_idx = DataGroup.label_titles.index(DataGroup.label_is_check)
            print(rowIdx, column_idx, item[DataGroup.attr_is_check])
            self.table_widget.setCellWidget(rowIdx, column_idx, self.create_cell_widget(column_idx, item[DataGroup.attr_is_check]))
            column_idx = DataGroup.label_titles.index(DataGroup.label_text_name)
            self.table_widget.setItem(rowIdx, column_idx, self.create_cell_widget(column_idx, item[DataGroup.attr_text_name]))
            #column_idx = DataGroup.label_titles.index(DataGroup.label_num_reapeat)
            #self.table_widget.setItem(rowIdx, column_idx, self.create_cell_widget(column_idx, item[DataGroup.attr_num_reapeat]))
            column_idx = DataGroup.label_titles.index(DataGroup.label_btn_up)
            self.table_widget.setCellWidget(rowIdx, column_idx, self.create_widget_up())
            column_idx = DataGroup.label_titles.index(DataGroup.label_btn_down)
            self.table_widget.setCellWidget(rowIdx, column_idx, self.create_widget_down())

    #위젯 생성
    def create_cell_widget(self, columnIndex, val):
        if DataGroup.label_titles[columnIndex] ==  DataGroup.label_is_check:
            cell_widget = QtWidgets.QWidget()
            chk_bx = QtWidgets.QCheckBox()
            chk_bx.setCheckState(val)
            chk_bx.stateChanged.connect(self.ev_cell_changed_checkbox)
            lay_out = QtWidgets.QHBoxLayout(cell_widget)
            lay_out.addWidget(chk_bx)
            lay_out.setAlignment(QtCore.Qt.AlignCenter)
            lay_out.setContentsMargins(0,0,0,0)
            return cell_widget

        else:
            return QtWidgets.QTableWidgetItem(val)    

    #UP 버튼 
    def create_widget_up(self):
        btn_up = QtWidgets.QPushButton("UP")
        btn_up.clicked.connect(self.ev_cell_up)
        return btn_up

    #DOWN 버튼 
    def create_widget_down(self):
        btn_down = QtWidgets.QPushButton("DOWN")
        btn_down.clicked.connect(self.ev_cell_down)
        return btn_down

    #cell up
    def ev_cell_up(self):
        btn_up = self.table_widget.sender()
        item = self.table_widget.indexAt(btn_up.pos())
        print("확인", item.row())
        row_index = item.row()
        if row_index > 0:
            self.group_list[row_index-1], self.group_list[row_index] = self.group_list[row_index], self.group_list[row_index-1]

        self.bind_items()
    
    #cell down
    def ev_cell_down(self):
        btn_down = self.table_widget.sender()
        item = self.table_widget.indexAt(btn_down.pos())
        print("확인", item.row())

        row_index = item.row()
        if len(self.group_list)-1 > row_index:
            self.group_list[row_index+1], self.group_list[row_index] = self.group_list[row_index], self.group_list[row_index+1]
        
        self.bind_items()

    #저장
    def ev_save(self):
        self.cb_save()

    #전체선택
    def ev_changed_checkbox_all(self, state):
        if state == QtCore.Qt.CheckState.Checked:
            for item in self.group_list:
                item[DataGroup.attr_is_check] = True
        else: 
            for item in self.group_list:
                item[DataGroup.attr_is_check] = False
        self.bind_items()

    #행 추가 
    def ev_add_row(self):
        group = copy.deepcopy(DataGroup.attr)
        self.group_list.append(group)
        self.bind_items()

    #선택 실행
    def ev_run_group(self):
        run_list = []
        for group in self.group_list:
            if group[DataGroup.attr_is_check] == True:
                run_list += group[DataGroup.attr_job_list]
        self.cb_run_group(run_list)

    #선택 삭제
    def ev_del_group(self):
        for group in reversed(self.group_list):
            if group[DataGroup.attr_is_check] == True:
                self.group_list.remove(group)
        self.bind_items()
        self.cb_clear_job()

    #cell 그룹 더블클릭 
    def ev_cell_double_click(self):
        self.table_widget.selectRow(self.table_widget.currentIndex().row())
        #load deatil
        self.cb_load_job(self.table_widget.currentIndex().row())

    #cell change 체크박스
    def ev_cell_changed_checkbox(self, int):
        checkbox = self.table_widget.sender()
        item = self.table_widget.indexAt(checkbox.parent().pos())
        self.group_list[item.row()][DataGroup.attr_is_check] = checkbox.isChecked()
        print(self.group_list)

    #cell change text
    def ev_cell_change_text(self, row, col):
        data = self.table_widget.item(row, col)
        if DataGroup.label_titles[col] == DataGroup.label_text_name:
            self.group_list[row][DataGroup.attr_text_name] = data.text()
        #elif DataGroup.label_titles[col] == DataGroup.label_num_reapeat:
        #    self.group_list[row][DataGroup.attr_num_reapeat] = data.text()


#레이아웃 job
class LayoutJob():
    def __init__(self, callbck_sel_run) -> None:
        
        self.table_widget = QtWidgets.QTableWidget()
        self.callbck_sel_run = callbck_sel_run
        self.item_list = None

    def create_layout(self):
        '''
        작업 리스트 
        작업이름 | 행 추가
        rows
        전체선택 | 선택 실행 | 선택 삭제
        '''
        result_layout = QtWidgets.QVBoxLayout()
        lb_title = QtWidgets.QLabel("작업 이름")
        result_layout.addWidget(lb_title)
        #상단
        top_layout = QtWidgets.QHBoxLayout()
        
        btn_add = QtWidgets.QPushButton("행 추가")
        
        top_layout.addStretch(1)
        top_layout.addWidget(btn_add)
        result_layout.addLayout(top_layout)
        #상단-이벤트
        btn_add.clicked.connect(self.ev_add_row)
        

        #중단 테이블
        result_layout.addWidget(self.table_widget)

        self.table_widget.horizontalHeader().setSectionResizeMode(1)
        self.table_widget.setColumnCount(len(DataJob.label_titles))
        self.table_widget.setHorizontalHeaderLabels(DataJob.label_titles)
        
        self.table_widget.cellChanged.connect(self.ev_cell_change_text)

        #하단
        bottom_layout = QtWidgets.QHBoxLayout()
        cb_all_select = QtWidgets.QCheckBox('전체선택')
        btn_run = QtWidgets.QPushButton("선택 실행")
        btn_del = QtWidgets.QPushButton("선택 삭제")
        bottom_layout.addWidget(cb_all_select)
        bottom_layout.addWidget(btn_run)
        bottom_layout.addWidget(btn_del)
        result_layout.addLayout(bottom_layout)

        cb_all_select.stateChanged.connect(self.ev_all_select)
        btn_run.clicked.connect(self.ev_run_job)
        btn_del.clicked.connect(self.ev_del_job)
        
        return result_layout

    def set_item_list(self, item_list):
        self.item_list = item_list

    def bind_items(self):
        self.table_widget.setRowCount(len(self.item_list))
        self.table_widget.setColumnCount(len(DataJob.label_titles))

        #print("bind", self.item_list)
        for rowIdx, item in enumerate(self.item_list):
            column_idx = DataJob.label_titles.index(DataJob.label_is_check)
            self.table_widget.setCellWidget(rowIdx, column_idx, self.create_cell_widget(column_idx, item[DataJob.attr_is_check]))

            column_idx = DataJob.label_titles.index(DataJob.label_job_name)
            self.table_widget.setItem(rowIdx, column_idx, self.create_cell_widget(column_idx, item[DataJob.attr_job_name]))

            column_idx = DataJob.label_titles.index(DataJob.label_type_target)
            self.table_widget.setCellWidget(rowIdx, column_idx, self.create_cell_widget(column_idx, item[DataJob.attr_type_target]))

            column_idx = DataJob.label_titles.index(DataJob.label_text_target)
            self.table_widget.setItem(rowIdx, column_idx, self.create_cell_widget(column_idx, item[DataJob.attr_text_target]))

            column_idx = DataJob.label_titles.index(DataJob.label_type_action)
            self.table_widget.setCellWidget(rowIdx, column_idx, self.create_cell_widget(column_idx, item[DataJob.attr_type_action]))

            column_idx = DataJob.label_titles.index(DataJob.label_type_selector)
            self.table_widget.setCellWidget(rowIdx, column_idx, self.create_cell_widget(column_idx, item[DataJob.attr_type_selector]))

            column_idx = DataJob.label_titles.index(DataJob.label_text_selector)
            self.table_widget.setItem(rowIdx, column_idx, self.create_cell_widget(column_idx, item[DataJob.attr_text_selector]))

            column_idx = DataJob.label_titles.index(DataJob.label_text_input)
            self.table_widget.setItem(rowIdx, column_idx, self.create_cell_widget(column_idx, item[DataJob.attr_text_input]))

            column_idx = DataJob.label_titles.index(DataJob.label_btn_confirm)
            self.table_widget.setCellWidget(rowIdx, column_idx, self.create_widget_confirm())

            column_idx = DataJob.label_titles.index(DataJob.label_btn_up)
            self.table_widget.setCellWidget(rowIdx, column_idx, self.create_widget_up())

            column_idx = DataJob.label_titles.index(DataJob.label_btn_down)
            self.table_widget.setCellWidget(rowIdx, column_idx, self.create_widget_down())

    #확인 버튼 
    def create_widget_confirm(self):
        btn_confirm = QtWidgets.QPushButton("확인")
        btn_confirm.clicked.connect(self.ev_cell_confirm)
        return btn_confirm
    
    #위로 버튼 
    def create_widget_up(self):
        btn_up = QtWidgets.QPushButton("UP")
        btn_up.clicked.connect(self.ev_cell_up)
        return btn_up

    #아래로 버튼 
    def create_widget_down(self):
        btn_down = QtWidgets.QPushButton("DOWN")
        btn_down.clicked.connect(self.ev_cell_down)
        return btn_down

    def create_cell_widget(self, columnIndex, val):
        if DataJob.label_titles[columnIndex] == DataJob.label_is_check:
            cell_widget = QtWidgets.QWidget()
            chk_bx = QtWidgets.QCheckBox()
            chk_bx.setCheckState(val)
            chk_bx.stateChanged.connect(self.ev_cell_change_checkbox)
            lay_out = QtWidgets.QHBoxLayout(cell_widget)
            lay_out.addWidget(chk_bx)
            lay_out.setAlignment(QtCore.Qt.AlignCenter)
            lay_out.setContentsMargins(0,0,0,0)
            return cell_widget

        elif DataJob.label_titles[columnIndex] == DataJob.label_type_selector:
            cb = QtWidgets.QComboBox()
            cb.addItems(TypeSelector.list)
            cb.setCurrentText(val)
            cb.currentIndexChanged.connect(self.ev_cell_change_combo)
            return cb

        elif DataJob.label_titles[columnIndex] == DataJob.label_type_action:
            cb = QtWidgets.QComboBox()
            cb.addItems(TypeAction.list)
            cb.setCurrentText(val)
            cb.currentIndexChanged.connect(self.ev_cell_change_combo)
            return cb

        elif DataJob.label_titles[columnIndex] == DataJob.label_type_target:
            cb = QtWidgets.QComboBox()
            cb.addItems(TypeTarget.list)
            cb.setCurrentText(val)
            cb.currentIndexChanged.connect(self.ev_cell_change_combo)
            return cb

        else:
            text_item = QtWidgets.QTableWidgetItem(val)
            return text_item

    #로우 추가
    def ev_add_row(self):
        if self.item_list == None:
            msgBox = QtWidgets.QMessageBox()
            msgBox.setIcon(QtWidgets.QMessageBox.Information)
            msgBox.setText("그룹 선택후 활성화 됩니다.")
            msgBox.setWindowTitle("확인")
            msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msgBox.exec()
            return

        job = copy.deepcopy(DataJob.attr)
        self.item_list.append(job)
        self.bind_items()

    #실행
    def ev_run_job(self):
        run_list = []
        for item in self.item_list:
            if item[DataJob.attr_is_check] == True:
                run_list.append(item)
        
        self.callbck_sel_run(run_list)
        print('click run')

    #삭제
    def ev_del_job(self):
        for item in reversed(self.item_list):
            if item[DataJob.attr_is_check] == True:
                self.item_list.remove(item)
        self.bind_items()
        print('click del')
    
    #전체 선택 
    def ev_all_select(self, state):
        if self.item_list == None:
            return
        if state == QtCore.Qt.CheckState.Checked:
            for item in self.item_list:
                item[DataJob.attr_is_check] = True
        else: 
            for item in self.item_list:
                item[DataJob.attr_is_check] = False
        self.bind_items()

    #cell 확인
    def ev_cell_confirm(self):
        btn_confirm = self.table_widget.sender()
        item = self.table_widget.indexAt(btn_confirm.pos())
        print("확인", item.row())

        run_list = []
        run_list.append(self.item_list[item.row()]) 
        self.callbck_sel_run(run_list)

    #cell up
    def ev_cell_up(self):
        btn_up = self.table_widget.sender()
        item = self.table_widget.indexAt(btn_up.pos())
        print("확인", item.row())
        row_index = item.row()
        if row_index > 0:
            self.item_list[row_index-1], self.item_list[row_index] = self.item_list[row_index], self.item_list[row_index-1]

        self.bind_items()
    
    #cell down
    def ev_cell_down(self):
        btn_down = self.table_widget.sender()
        item = self.table_widget.indexAt(btn_down.pos())
        print("확인", item.row())

        row_index = item.row()
        if len(self.item_list)-1 > row_index:
            self.item_list[row_index+1], self.item_list[row_index] = self.item_list[row_index], self.item_list[row_index+1]
        
        self.bind_items()
    
    #cell change 체크박스
    def ev_cell_change_checkbox(self, int):
        checkbox = self.table_widget.sender()
        print(int)
        item = self.table_widget.indexAt(checkbox.parent().pos())
        self.item_list[item.row()][DataJob.attr_is_check] = checkbox.isChecked()
        #print(self.item_list)
    
    #cell change 콤보
    def ev_cell_change_combo(self, value):
        
        combo = self.table_widget.sender()
        item = self.table_widget.indexAt(combo.pos())
        
        if DataJob.label_titles[item.column()] == DataJob.label_type_selector:
            self.item_list[item.row()][DataJob.attr_type_selector] = combo.currentText()
        elif DataJob.label_titles[item.column()] == DataJob.label_type_action:
            self.item_list[item.row()][DataJob.attr_type_action] = combo.currentText()
        elif DataJob.label_titles[item.column()] == DataJob.label_type_target:
            self.item_list[item.row()][DataJob.attr_type_target] = combo.currentText()
        
        #print(self.item_list)

    #cell change text 
    def ev_cell_change_text(self, row, col):
        data = self.table_widget.item(row, col)

        if DataJob.label_titles[col] == DataJob.label_job_name:
            self.item_list[row][DataJob.attr_job_name] = data.text()
        elif DataJob.label_titles[col] == DataJob.label_text_target:
            self.item_list[row][DataJob.attr_text_target] = data.text()
        elif DataJob.label_titles[col] == DataJob.label_text_selector:
            self.item_list[row][DataJob.attr_text_selector] = data.text()
        elif DataJob.label_titles[col] == DataJob.label_text_input:
            self.item_list[row][DataJob.attr_text_input] = data.text()
        
        #print(self.item_list)

if __name__ == "__main__":
    job_q = Queue()
    result_q = Queue()
    app = QtWidgets.QApplication(sys.argv)
    dm = QtGui(job_q, result_q)

    dm.show()
    app.exit((app.exec_()))