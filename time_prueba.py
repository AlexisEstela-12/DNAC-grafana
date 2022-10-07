from datetime import datetime

x = "17:19"

def get_hora_format(time):
    get_hora = datetime.strptime(time,"%H/%M")
    print(get_hora)
    return(get_hora)


print(get_hora_format(x))