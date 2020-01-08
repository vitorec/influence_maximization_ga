import os
from os import sep as separator


def parse_file_path(filepath):
	path = os.path.dirname(filepath).replace('/', separator)
	name = os.path.basename(filepath).rsplit('.', 1)[0]
	extension = filepath.rsplit('.', 1)[1]
	uri = path + separator + name
	return path, name, extension, uri


def binary_search(item_list, item):
	first = 0
	last = len(item_list) - 1
	found = False
	while first <= last and not found:
		mid = (first + last) // 2
		if item_list[mid] == item:
			found = True
		else:
			if item < item_list[mid]:
				last = mid - 1
			else:
				first = mid + 1
	return found

