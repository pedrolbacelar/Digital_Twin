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
- 
