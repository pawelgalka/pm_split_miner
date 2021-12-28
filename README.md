# SPLIT MINER

## Authors: Paweł Gałka, Marcin Grzyb, Wojciech Sałapatek

Project created for PM class in AGH UST

### Run:

- Compile Java Joiner (if not present under `/java-joiner/target/JoinMiner.jar`): `mvn clean install`
  
  *Note*: requires JDK 11 to run
- Run Python script : `python3 main.py`

  *Note* input log must be placed within `data` folder as XES file. Output PNG image will be placed in `output`
  directory.

### References:

- [Split miner: automated discovery of accurate and simple business process models from event logs](https://www.researchgate.net/publication/325157122_Split_miner_automated_discovery_of_accurate_and_simple_business_process_models_from_event_logs)
- [Split Miner: Discovering Accurate and Simple Business Process Models from Event Logs](https://kodu.ut.ee/~dumas/pubs/icdm2017-split-miner.pdf)
- [JBPT library](https://github.com/jbpt/codebase)