# SPLIT MINER

## Authors: Paweł Gałka, Marcin Grzyb, Wojciech Sałapatek

Project created for Process Mining course at AGH UST ([Syllabus link](https://sylabusy.agh.edu.pl/en/document/de672e22-d826-48a3-af06-fe7d8d7d8503.pdf))

### Run:

- Compile Java Joiner (folder `java-joiner`), (if not present under `/java-joiner/target/JoinMiner.jar`): `mvn clean install`
  
  *Note*: requires JDK 11 to run

  Usage of Java was required due to lack of native Python libraries regarding BPMN RPST processing

- Run Python script : `python3 main.py`

  *Note* input log must be placed within `data` folder as XES file. Output PNG image will be placed in `output`
  directory.

- Usage: main.py [-h] [--eta ETA] [--epsilon EPSILON] --log_name LOG_NAME

  This script is doing Split Mining of given XES file
  
  optional arguments:
  - -h, --help           show this help message and exit
  - --eta ETA            Value of filtering threshold from DFG to PDFG
  - --epsilon EPSILON    Value of percentile during discovery of concurrent and
                         infrequent tasks
  - --log_name LOG_NAME  Log name in data folder

### References:

- [Split miner: automated discovery of accurate and simple business process models from event logs](https://www.researchgate.net/publication/325157122_Split_miner_automated_discovery_of_accurate_and_simple_business_process_models_from_event_logs)
- [Split Miner: Discovering Accurate and Simple Business Process Models from Event Logs](https://kodu.ut.ee/~dumas/pubs/icdm2017-split-miner.pdf)
- [JBPT library](https://github.com/jbpt/codebase)