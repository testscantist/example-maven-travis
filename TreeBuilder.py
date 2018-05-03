import json
import os
import subprocess
import xml.etree.ElementTree as XMLParser

JAVA_COMPILE = "jar"
TRAVIS_LOG_FILE = "raw-output.txt"
DEPENDENCY_CONNECTOR = ":"
MAVEN_PACKAGE_MANAGER = "mvn"
MAVEN_POM_FILE_NAME = "pom.xml"
MAVEN_NAMESPACE = "{http://maven.apache.org/POM/4.0.0}"
MAVEN_LOG_PREFIX = "[INFO] "
MAVEN_ENDLING_LINE = "[INFO] ------------------------------------------------------------------------"
GRADLE_PACKAGE_MANAGER = "gradle"
GRADLE_BUILD_FILE_NAME = "build.gradle"
GRADLE_CONFIG_MODE = "compile"
GRADLE_LOG_PREFIX = ""
GRADLE_CONNECTOR = " - "
GRADLE_STARTING_LINE = "Dependencies for source set 'main' (deprecated, use 'implementation ' instead)."
GRADLE_ENDLING_LINE = "\n"


class Node:
    def __init__(self, data):
        self.parent = None
        self.level = 0
        self.data = data
        self.children = []

    def getData(self):
        return self.data

    def getChildren(self):
        return self.children

    def getLevel(self):
        return self.level

    def getParent(self):
        return self.parent

    def addChild(self, node):
        if(self.__class__ == node.__class__):
            node.parent = self
            node.level = self.level + 1
            self.children.append(node)

    def equals(self, other):
        if(self.__class__ == other.__class__):
            if(self.data == other.data):
                return True
        return False

    def contains(self, other):
        found = False
        if self.__class__ == other.__class__:
            if self.data == other.data:
                found = True
            else:
                for child in self.children:
                    found = child.contains(other)
                    if found:
                        break
        return found

    def find(self, other):
        foundNode = None
        if(self.__class__ == other.__class__):
            if(self.data == other.data):
                foundNode = self
            else:
                for child in self.children:
                    foundNode = child.find(other)
                    if foundNode:
                        break
        return foundNode

    def toString(self, tabulate):
        tabs = ' '
        if tabulate:
            tabs += (self.level+1)*'  '
        return str(self.level) + tabs + self.data + '\n'

    def buildWithChildren(self, tabulate):
        result = self.toString(tabulate)
        for child in self.children:
            result += child.buildWithChildren(tabulate)
        return result

    def buildWithChildrenToDict(self, tabulate, package_manager):
        if package_manager == MAVEN_PACKAGE_MANAGER:
            version_index = 3
        if package_manager == GRADLE_PACKAGE_MANAGER:
            version_index = 2
        plain_text = self.toString(tabulate)

        plain_text_start_with_library = plain_text.rfind(
            ' ')+1 if self.level == 0 else plain_text.rfind('- ')+2
        plain_text = plain_text[plain_text_start_with_library:]
        end_index_of_library = plain_text.find(
            ' ') if plain_text.find(' ') > 0 else -1
        plain_text = plain_text[:end_index_of_library]
        key_values = plain_text.split(":")
        result = {
            "group_id": key_values[0],
            "artifact_id": key_values[1],
            "version": key_values[version_index],
            "level": self.level,
            "children": []
        }
        for child in self.children:
            result["children"].append(
                child.buildWithChildrenToDict(tabulate, package_manager))
        return result

    def buildWithAncestors(self, tabulate):
        result = ''
        if(self.parent is not None):
            result = self.parent.buildWithAncestors(tabulate)
        return result + self.toString(tabulate)


class Tree:
    def __init__(self, root, package_manager):
        self.root = root
        self.package_manager = package_manager

    def getRoot(self):
        return self.root

    def contains(self, node):
        return self.root.contains(node)

    def find(self, node):
        return self.root.find(node)

    def toString(self, tabulate):
        return self.root.buildWithChildren(tabulate)

    def buildWithChildrenToDict(self, tabulate):
        return self.root.buildWithChildrenToDict(tabulate, self.package_manager)


class TreeParser:
    def __init__(self, data, rootName, starting_line, ending_line):
        self.data = data
        self.rootName = rootName
        self.starting_line = starting_line
        self.ending_line = ending_line

    def parse(self):
        treeStart = self.starting_line
        treeEnd = self.ending_line

        with open(self.data) as f:
            content = f.read()

        print('inside TreeParser')
        # print('content: ')
        # print(content)
        # print('treestart:')
        # print(treeStart)

        rawTree = str.split(content, treeStart+'\n', 1)[1]
        # print(rawTree)
        rawTree = str.split(rawTree, '\n' + treeEnd, 1)[0]
        # print(rawTree)
        nodeList = str.split(rawTree, '\n')
        print('nodeList: ')
        print(nodeList)

        return nodeList


class TreeBuilder:
    def __init__(self, data, rootName, starting_line, ending_line, package_manager):
        self.data = data
        self.rootName = rootName
        self.starting_line = starting_line
        self.ending_line = ending_line
        self.root = Node(self.rootName)
        self.tree = Tree(self.root, package_manager)

    def computeLevel(self, rawNode):
        level = 1
        for c in rawNode:
            if(c == '|'):
                level = level + 1
            elif(c == '+' or c == '\\'):
                break
        return level

    def build(self):
        nodeList = TreeParser(self.data, self.rootName,
                              self.starting_line, self.ending_line).parse()
        parent = self.root

        for rawNode in nodeList:
            level = self.computeLevel(rawNode)
            child = Node(rawNode)
            while(parent.getLevel() >= level):
                parent = parent.getParent()
            parent.addChild(child)
            parent = child

        return self.tree


class Project(object):
    def __init__(self, group_id, artifact_id, version, package_manager, config_mode, packaging):
        self.group_id = group_id
        self.artifact_id = artifact_id
        self.version = version
        self.package_manager = package_manager
        self.config_mode = config_mode
        self.parent = None
        self.packaging = packaging

        self._id = None

    @property
    def id(self):
        if self._id is None:
            self._id = (self.group_id, self.artifact_id)
        return self._id

    def get_root_name(self):
        if self.package_manager == MAVEN_PACKAGE_MANAGER:
            return MAVEN_LOG_PREFIX + self.group_id + DEPENDENCY_CONNECTOR + \
                self.artifact_id + DEPENDENCY_CONNECTOR + \
                JAVA_COMPILE + DEPENDENCY_CONNECTOR + self.version
        if self.package_manager == GRADLE_PACKAGE_MANAGER:
            return GRADLE_LOG_PREFIX+self.group_id + DEPENDENCY_CONNECTOR + \
                DEPENDENCY_CONNECTOR + self.version

    def get_starting_line(self):
        if self.package_manager == MAVEN_PACKAGE_MANAGER:
            return MAVEN_LOG_PREFIX + self.group_id + DEPENDENCY_CONNECTOR + \
                self.artifact_id + DEPENDENCY_CONNECTOR + \
                self.packaging + DEPENDENCY_CONNECTOR + self.version
        if self.package_manager == GRADLE_PACKAGE_MANAGER:
            return GRADLE_LOG_PREFIX + self.config_mode + GRADLE_CONNECTOR + \
                GRADLE_STARTING_LINE

    def get_endling_line(self):
        if self.package_manager == MAVEN_PACKAGE_MANAGER:
            return MAVEN_ENDLING_LINE
        if self.package_manager == GRADLE_PACKAGE_MANAGER:
            return GRADLE_ENDLING_LINE

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)


def main(args):
    print('-----------------inside TreeBuilder--------------------')
    print(args)
    current_path = args[0]
    repo_name = args[1]
    commit_sha = args[2]

    project = initialize_project(current_path)
    if project is None:
        print("cannot find project")
        return
    root_name = project.get_root_name()
    ending_line = project.get_endling_line()
    starting_line = project.get_starting_line()
    package_manager = project.package_manager
    print(root_name)
    print(ending_line)
    print(starting_line)
    print(package_manager)
    generate_package_manager_log(project)
    data_file_path = os.path.join(current_path, TRAVIS_LOG_FILE)
    if os.path.isfile(data_file_path):
        print('datafile exists')
        data_file = TRAVIS_LOG_FILE
        tree = TreeBuilder(data_file, root_name, starting_line,
                           ending_line, package_manager).build()
        tree_data = tree.buildWithChildrenToDict(False)
        tree_data['repo_name'] = repo_name
        tree_data['commit_sha'] = commit_sha

        with open('dependency-tree.json', 'w') as outfile:
            json.dump(tree_data, outfile)


def initialize_project(current_path):
    # find pom file in current folder
    init_project = None

    pom_file_path = os.path.join(current_path, MAVEN_POM_FILE_NAME)
    gradle_file_path = os.path.join(current_path, GRADLE_BUILD_FILE_NAME)

    if os.path.isfile(pom_file_path):
        init_project = get_project_from_pom(pom_file_path)
    elif os.path.isfile(gradle_file_path):
        init_project = get_project_from_gradle(gradle_file_path)
    return init_project


def get_project_from_pom(pom_path):
    pom = XMLParser.parse(pom_path)
    root = pom.getroot()
    group_id = ''
    artifact_id = ''
    version = ''
    package_manager = MAVEN_PACKAGE_MANAGER
    config_mode = None
    packaging = JAVA_COMPILE
    for item in root.getchildren():
        if item.tag == MAVEN_NAMESPACE + 'groupId':
            group_id = item.text
        if item.tag == MAVEN_NAMESPACE + 'artifactId':
            artifact_id = item.text
        if item.tag == MAVEN_NAMESPACE + 'version':
            version = item.text
        if item.tag == MAVEN_NAMESPACE + 'packaging':
            packaging = item.text

    if group_id is None:
        raise Exception('Missing groupId')
    if artifact_id is None:
        raise Exception('Missing artifactId')
    if version is None:
        raise Exception('Missing artifactId')

    project = Project(group_id, artifact_id, version,
                      package_manager, config_mode, packaging)

    return project


def get_project_from_gradle(gradle_path):
    # pom = XMLParser.parse(gradle_path)
    # root = pom.getroot()
    group_id = "com.test.name"
    artifact_id = None
    version = "0.1.0.snapshot"
    package_manager = GRADLE_PACKAGE_MANAGER
    config_mode = GRADLE_CONFIG_MODE
    packaging = JAVA_COMPILE

    project = Project(group_id, artifact_id, version,
                      package_manager, config_mode, packaging)

    return project


def generate_package_manager_log(project):
    print('-----------------generate_package_manager_log--------------------')
    if project.package_manager == MAVEN_PACKAGE_MANAGER:
        result = subprocess.run(
            ['mvn', '-B', 'dependency:tree'], stdout=subprocess.PIPE).stdout.decode('utf-8')
        with open(TRAVIS_LOG_FILE, 'w') as outfile:
            outfile.write(result)
        return True
    if project.package_manager == GRADLE_PACKAGE_MANAGER:
        result = subprocess.run(['gradle', 'dependencies', '--configuration',
                                 project.config_mode], stdout=subprocess.PIPE).stdout.decode('utf-8')
        with open(TRAVIS_LOG_FILE, 'w') as outfile:
            outfile.write(result)
        return True
    return False


if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
