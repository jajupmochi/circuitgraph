# Circuitgraph Insights
This repository contains both sourcecode and forward chaining rules for knowledge inference in electrical circuit diagrams.

# Building the Engine
```
insights/engine$ mvn package
```

# Running the Engine
```
insights$ java -jar engine/target/circuit-inference-0.0.1.jar  --input=../test/C177.ttl --output=../test/C177_process_test.ttl
```
