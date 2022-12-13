
class TypeSelector:
    empty = ""
    xpath = "xpath"
    id = "id"
    class_ = "class"
    query_selector = "query_selector"
    list = [empty, xpath, id, class_, query_selector]
    
class TypeAction:
    empty = ""
    click = "click"
    get = "get"
    set = "set"
    list = [empty, click, get, set]

class TypeTarget:
    single = "single"
    multiple = "multiple"
    url = "url"
    frame = "frame"
    list = [single, multiple, url, frame]

class DataJob:
    attr_idx = "idx"
    attr_job_name = "job_name"
    attr_is_check = "is_check"
    attr_text_target = "text_target"
    attr_text_selector = "text_selector"
    attr_type_selector = "type_selector"
    attr_type_action = "type_action"
    attr_type_target = "type_target"
    attr_text_input = "text_input"
    attr_text_result = "text_result"

    attr = { 
        attr_idx: '',
        attr_is_check: False,
        attr_job_name: '',
        attr_text_target: '',
        attr_text_selector: '',
        attr_type_selector: TypeSelector.empty,
        attr_type_action: TypeAction.empty,
        attr_type_target: TypeTarget.single,
        attr_text_input: '',
        attr_text_result: '',
    }

    label_is_check = '선택'
    label_job_name = '이름'
    label_type_target = 'Target구분'
    label_text_target = 'Target정보'
    label_type_action = '액션_구분'
    label_type_selector = '선택자구분'
    label_text_selector = '선택자'
    label_text_input = 'input'
    label_btn_confirm = '확인'
    label_btn_up = '위로'
    label_btn_down = '아래로'

    label_titles = [label_is_check, label_job_name, label_type_target, label_text_target, label_type_action,  label_type_selector, label_text_selector, label_text_input, label_btn_confirm, label_btn_up, label_btn_down]


class DataGroup:
    attr_idx = "idx"
    attr_is_check = "is_check"
    attr_text_name = "text_name"
    attr_num_reapeat = "num_reapeat"
    attr_job_list = "job_list"

    attr = { 
        attr_idx: '',
        attr_is_check: False,
        attr_text_name: '',
        attr_num_reapeat: '',
        attr_job_list : []
    }

    label_is_check = '선택'
    label_text_name = '이름'
    #label_num_reapeat = '반복횟수'
    label_btn_up = '위로'
    label_btn_down = '아래로'
    label_titles = [label_is_check, label_text_name, label_btn_up, label_btn_down]

