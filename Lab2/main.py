import json

print(json.dumps(
    {
        'bookstore': [
            {
                "title": {
                    'lang': 'Introduction',

                }
            }
        ]
    }
))

a = {
    "a": "b",
    "c": "d"
}
b = {
    "c": "d",
    "a": "b"
}
print(a == b)

print([1,2]==[2,1])


import xml.etree.ElementTree as ET
root = ET.Element('person')
name = ET.SubElement(root, 'name')
name.text = 'Cristina'
age = ET.SubElement(root, 'age')
age.text = '20'
isStudent = ET.SubElement(root, 'isStudent')
isStudent.text = 'True'
xml_data = ET.tostring(root).decode()
print(xml_data)












































