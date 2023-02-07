import sys
import re
class cif_structure():
    replace_map = {"0.500000":"1/2","0.250000":"1/4","0.750000":"3/4","0.333333":"1/3","0.666667":"2/3","0":"0"}
    def __init__(self,name,x,y,z,char) -> None:
        self.name = name
        self.x = x
        self.y = y
        self.z = z
        self.char = char

    def coord_replace(self,coord):
        for key in self.replace_map.keys():
            if float(coord) == float(key):
                return self.replace_map[key]
        return coord
    def selfFraqReplace(self):
        self.x = self.coord_replace(self.x)
        self.y = self.coord_replace(self.y)
        self.z = self.coord_replace(self.z)

    def selfCheck(self) -> bool:
        return self.name != None and self.x != None and self.y != None and self.z != None and self.char != None
    def getFormatted(self):
        return '{"' + self.name + '",{'+ self.x + "," + self.y + "," + self.z + "}," +  self.char + "}" 
    def __repr__(self) -> str:
        return self.name + " " + self.x + " " + self.y + " " + self.z + " " + self.char


def handle_loop(f,line,cif_list):
    lines_map = []
    line = f.readline()
    while "_atom" in line:
            lines_map.append(line)
            line = f.readline()
    name_index = -1
    x_index = -1
    y_index = -1
    z_index = -1
    char_index = -1
    for i in range(0,len(lines_map)):
        if "_atom_site_type_symbol" in lines_map[i]:
            name_index = i
        if "_atom_site_fract_x" in lines_map[i]:
            x_index = i
        if "_atom_site_fract_y" in lines_map[i]:
            y_index = i
        if "_atom_site_fract_z" in lines_map[i]:
            z_index = i
        if  "_atom_site_adp_type" in lines_map[i]:
            char_index = i
    if name_index == -1 or x_index == -1 or y_index == -1 or z_index == -1 or char_index == -1:
        return False
    cut = lambda x: x if "(" not in x else x.split("(")[0]
    while len(line) > 4 and not line.startswith("#"): 
        splited = line.split()
        name = splited[name_index]
        m = re.search(r"\d", name)
        if m:
            name = name[:m.start()]
        x = cut(splited[x_index])
        y = cut(splited[y_index])
        z = cut(splited[z_index])
        new_atom = cif_structure(name,x,y,z,splited[char_index])
        new_atom.selfFraqReplace()
        if not new_atom.selfCheck():
            raise Exception("error cif(" + cif_f + ") file parsing: line error parsing: ", line)
        cif_list.append(new_atom)
        line = f.readline()
    return True
if __name__ == "__main__":
    try:
        cif_f = "wrong_cif.cif"
        feop = "beb.sym"
    except Exception as e:
        print("Expected: python3", sys.argv[0], "cif_filepath sym_filepath")
        raise
    cif_list =[]
    try:
        with open(cif_f) as f:
            line = f.readline()
            while line:
                if "loop_" in line:
                    res = handle_loop(f,line,cif_list)
                    if res:
                        break
                    else:
                        continue
                line = f.readline()
            if len(cif_list) == 0:
                raise Exception("error cif(" + cif_f + ") file parsing: Not found")
    except Exception as e:
        print("ERROR!",e)
        raise
    print("Cif file was read")         
    for elem in cif_list:
        print(elem)
    print("Lenght is", len(cif_list))
    print("Converting...")
    try:
        #backup
        outf = "out_file.txt"
        with open(feop) as f:
            with open(outf,"w") as out:
                line = f.readline()
                while line:
                    if "section structure_definition" in line:
                        out.write(line)
                        line = f.readline()
                        while line:
                            if "int nsort" in line:
                                sp_count = line.split("i")[0].count(" ")
                                tab_count = line.split("i")[0].count("\t")
                                spaces = sp_count if sp_count>0 else tab_count*4
                                old_nsort = line.split('=')[1].split(';')[0]
                                out.write(" "*spaces + "int nsort=" + str(len(cif_list)) + ";\n")
                                line = f.readline()
                                continue
                            if "wyckoff_positions[nsort]" in line:
                                out.write(line)
                                line = f.readline()
                                out.write(line)
                                line = f.readline()
                                sp_count = line.split("{")[0].count(" ")
                                tab_count = line.split("{")[0].count("\t")
                                spaces = sp_count if sp_count>0 else tab_count*4
                                for i in range(int(old_nsort)):
                                    line = f.readline()
                                first = True                           
                                for elem in cif_list:                                 
                                    formatted = elem.getFormatted()
                                    if first:
                                        out.write(" "*spaces + elem.getFormatted() + '\n')
                                        first = False
                                    else:
                                        out.write(" "*spaces +',' + elem.getFormatted() + '\n')
                                break
                            out.write(line)
                            line = f.readline()                      
                    out.write(line)
                    line = f.readline()
    except Exception as e:
        print("ERROR!",e)
        raise
    print("File " + outf + " was successfully converted and saved")

