from setuptools import find_packages, setup
from typing import List

def get_requirements()-> List[str]:
    """This function is going to return list of requirements
    """
    requirement_list:List[str]=[]
    try:
        with open('requirements.txt', 'r') as file:
            lines= file.readlines()
            for line in lines:
                requirement=line.strip()
                if requirement and requirement!= '-e .': # ignore empty line and -e .
                    requirement_list.append(requirement)
                    
    except FileNotFoundError:
        print("Error: requirements.txt file not found.")
        
setup(
    name="Network_Security_system",
    version="0.0.1",
    author="Kshitij",
    author_email="kshitijk146@gmail.com",
    packages=find_packages(),
    install_requires=get_requirements()
)