def convertName(name):

    if name == 'Ammonia':
        name = 'NH$_3$'

    elif name == 'Acetileno':
        name = 'C$_2$H$_2$'

    elif name == 'Carbon Dioxide':
        name = 'CO$_2$'

    elif name == 'Carbon Monoxide':
        name = 'CO'

    elif name == 'Etileno':
        name = 'C$_2$H$_4$'

    elif name == 'Methane':
        name = 'CH$_4$'

    elif name == 'Nitric Oxide':
        name = 'NO'

    elif name == 'Balanca':
        name = 'Massa'

    elif name == 'O2':
        name = 'O$_2$'

    elif name == 'Pressao':
        name = 'Pressão'

    elif name == 'Temperatura_no_pleno':
        name = 'Tempreatura no pleno'

    elif name == 'vazao_ar' or name == 'vazao_ar_area':
        name = 'Fluxo de ar'
    
    elif name == 'tempoChama':
        name = 'Avanço da frente de chama'
    
    elif name == 'relacao_ar_esteq':
        name = 'Fluxo de Ar/Fluxo de Ar$_esteq$'

    return name

def getUnity(name):

    unity = ''

    if name == 'Ammonia' or name == 'Nitric Oxide':
        unity = 'ppm'

    elif name == 'Temperatura_no_pleno' or name == 'Temperatura':
        unity = '$^o$C'

    elif name == 'Balanca':
        unity = 'kg'

    elif name == 'Pressao':
        unity = 'Pa'

    elif name == 'vazao_ar':
        unity = 'kg/s'

    elif name == 'vazao_ar_area':
        name = 'kg/sm$^2$'

    elif name == 'tempoChama' or name == 'relacao_ar_esteq':
        unity = ''
    
    else:
        unity = '%'

    return unity