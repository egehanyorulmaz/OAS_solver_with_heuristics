#Utility functions

def list_separator(list_string):
    li = list(list_string.split(","))
    li = [float(i) for i in li]
    return li

def symmetrical_difference_positions(listA, listB):
    res = [listB.index(n) for m, n in
           zip(listA, listB) if n != m]
    return res


def element_exist_in_list(main_list, sub_list):
    """ Returns true if sub_list is already appended to the main_list. Otherwise returns false"""
    try:
        b = main_list.index(sub_list)
        return True
    except ValueError:
        return False