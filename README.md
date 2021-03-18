# Project ready

# Web server

> You can use this web server to elaborate data from gas sensors, particularly appa data. This project allow you to convert files "log" or "txt" into a powerful structure that contains entire dataset.
> You can choose to return pickle object, compress txt file or hdmf5 object.
> Also you can create line chart, useful to take a fast look on the datas.

# Indice

- [How to start](#How-to-start)
- [Which file can I process](#Which-file-can-I-process)
- [Manutenzione](#manutenzione)
- [Licenza](#licenza)

# How to start
You need to install a conda environment -> https://conda.io/projects/conda/en/latest/user-guide/install/index.html.
Then set up the environment installing with Python 3.8.8 or latest versions, and also install the following packages:
- Flask
- Numpy
- Tqdm
(Using command : conda install)
## Dipendenze
On linux ubuntu 20.04 or latest version works 100%, for windows should works but not sure 100%.
## How to install
Clone the repository in conda environment, what you need you find in web_app folder.

```git
git clone https://github.com/stefanichristian/dataSensor.git
```
Then you can run with python /dataSensor/web_app/app.py
or entering in the folder web_app and run python app.py

The server should start on port 5000

## Documentazione
### Link a documentazione esterna 

# Which file can you process
You can process this following type of files:
- .log
- .txt
- pickle object

Log file
> Log file must be in the format of appa
> ![Alt text](https://github.com/stefanichristian/dataSensor/blob/master/img_readme/appa.png)

Txt file
> Txt file must be in the format according with Dott. Andrea Gaiardo
Risc, Signal and Volt are the fields for each sensor. Temperature and humidity are the the fields that contain the data for the single session in that date. 

Pickle obj
> Pickle obj must be in the format which has first column as Data, and for each sensor must has "Risc", "Signal" and "Volt" columns, At the end must there are "Temp" (temperature) and "Hum" (humidity)  as last two columns.
As for txt file, Data format must be this : "Aug 27 2019 10:20:41"
## Installare le dipendenze di sviluppo

## Struttura del progetto

## Community

### Code of conduct

### Responsible Disclosure

### Segnalazione bug e richieste di aiuto

# Manutenzione 

# Licenza 

## Licenza generale 

## Autori e Copyright

## Licenze software dei componenti di terze parti
