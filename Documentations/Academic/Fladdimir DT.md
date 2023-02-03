# Review of Fladdmir Digital Twin Implementation

## References
- Documentation: https://fladdimir.github.io/post/csa-simulation-based-sc-forecast/
- Github: https://github.com/fladdimir/csa-simulation-based-sc-forecast
- Paper: [A brief introduction to deploy Amazon Web Services for online discrete-event simulation](https://www.researchgate.net/publication/359098225_A_brief_introduction_to_deploy_Amazon_Web_Services_for_online_discrete-event_simulation)

## Main Points

- The documentation give a good overview about the framework of the project and the main components used, even though there is no futher documentation on the Github repository and lack of examples about how to use the codes steps-by-step
- The overall focus of the project seems to be similar to Cycle Time prediction, but specific for prediction the impact on delay time of the raw material in the production process
- The paper and the project itself seems to be very focusing on the implementation of the system with AWS and online platforms
- They have some kind of way for visualizing the simulation and the results (probably using this  Casymda or some of the online tools showed in the documentation (plotly dash))
- They used "Tecnomatix Plant Simulation" and Simpy for creating the simulation model
- At least in the documentation there are no further explanation about how synchronization and validation were implemented.
- The steps to run the simulation doesn't seems generic for creating a different model

## Paper Higlight
- > _we present an intuitive and practice-oriented procedure model for deploying DES models on AWS._
- > _To the best of our knowledge, there are no publications to date that present an intuitive and  practice-oriented procedure model for deploying DES models on established cloud computing platforms. The present  work contributes to closing this gap_
- > _Every time the manufacturer requests material for producing a specific order (process step “Order Material”), an  initial estimated time of arrival (ETA) provides information on when  the requested material will be available for production._
- > _Casymda builds up on the DES Python package SimPy and the open-source BPMN modeler Camunda._
- > _We implement the process of Fig. 2 with the Python package Casymda_
- > _Casymda comes with a simple, yet powerful visualization concept  hat animates the movement of flow objects along  the simulated process and displays state changes of process blocks._
- > _we use Plotly Dash for visualizing results of the simulation. Plotly Dash is a popular framework for analytics web-apps. It allows a quick development of dynamic dashboards using the Python language_
- > _The complete cloud-based event-processing pipeline can be easily setup and run locally on the development machine using the tools Docker, Terraform and LocalStack_

- > _In future research, we plan to extend the problem to reach real-life complexity by introducing random process times, material inventories, and different order replenishment strategies into the use case._
- > _The resulting problem would particularly benefit from parallelized execution of simulation experiments to determine 
appropriate inventory management strategies in real time._

## Possibles Takeaways
- Use some tool like _Casymda_ or _Plotly Dash_ for visualizing the results and model of our simulation
- Analysizing the possibility to use some online cloud service for Database (what would be the gains and problems)
    - Sync would be easier?
- Analyze Cycle Time prediction within DES frameworks


## Framework

#### Main Components

<img src="https://user-images.githubusercontent.com/72768576/215736750-156e7ddc-6c1a-4fcc-8dd6-ad4fbcb59211.png" style="width:30%;">

#### Process Steps
<img src="https://user-images.githubusercontent.com/72768576/215736814-232ffeb2-1479-4d38-845a-14583a4bb902.png" style="width:50%;">

#### Digital Twin (shadow) framework
<img src="https://user-images.githubusercontent.com/72768576/215736968-70b392c4-2dfa-48a2-8dc5-e7b3e894b214.png" style="width:70%;">



