with open('vdiclient.ini', 'r') as file:
    lines = file.readlines()
    user_line = lines[43].replace("#", "").split(" ")
    user_line[2] = "lostmypillow" + "\n"
    token_name_line = lines[45].replace("#", "").split(" ")
    token_name_line[2] = "lostmypillow" + "\n"
    token_val_line = lines[47].replace("#", "").split(" ")
    token_val_line[2] = "245a4a7a-581f-434d-be48-e393d9578aa0" + "\n"
    vmid_line = lines[51].replace("#", "").split(" ")
    vmid_line[2] = "301" + "\n"

    lines[32] = '               "' + '192.168.3.32' + '" : ' + '8006' + '\n'
    lines[43] = " ".join(str(element) for element in user_line)
    lines[45] = " ".join(str(element) for element in token_name_line)
    lines[47] = " ".join(str(element) for element in token_val_line)
    lines[51] = " ".join(str(element) for element in vmid_line)


with open('vdiclient.ini', 'w') as file:
    file.writelines(lines)
