![image](https://user-images.githubusercontent.com/72768576/207659223-d59fc55f-36d0-4852-b84d-4881c4750746.png)

Start Controller and analyser 101

1- Open Supervisor and Supervisor_backbone DO NOT RUN FOR THE MOMENT

2- Check IP addresses and database name if correct, for example:
![image](https://user-images.githubusercontent.com/72768576/207659285-d49d2f76-b4e3-4ffc-b9ee-05f36354531f.png)

3- with moba start the lego system, in particular station 2 usually IP:….. 65 will be initialized with IMS.py (allows the feedback loop) while station 1 usually: identified by IP:….64 will be from initialize with IMS_test.py
4- Immediately after play on Supervisor_backbone to start broker, specifically the wording broker.active() is the one that activates the broker and therefore the writing of eventlog on database.
DO NOT START THE BROKER BEFORE STARTING BECAUSE there is an error on the mqtt start message


5- Wait until you have reached at least the 13th id on the eventlog.
6- In the console opened for Supervisor_backbone write: analyser.run() this allows the start of the calculation of the KPIs derived from the real.

7- Open a second console, start Supervisor
8- Once the Supervisor objects are created, write on the Supervisor console: controller.start()
![image](https://user-images.githubusercontent.com/72768576/207659327-c7ace03e-4153-4432-893b-562ad2dc97c2.png)


