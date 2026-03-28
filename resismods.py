import numpy as np
import cartopy.feature as cfeature

def csvread(name, year):
    import pandas as pd

    df = pd.read_csv(name+str(year)+'ari.csv')

    for i in df:
        if str(i)[:5]=='Unnam':
            df=df.drop(i, axis=1)

    return(df, name)



def add_data(year, state, data):
    text_file = open(year+state+".txt", "r")

    #read whole file to a string
    data2 = text_file.read()

    #close file
    text_file.close()

    data2 = data2.split("\n")
    n=0
    while n < len(data2):
        data2[n]=data2[n].split(',')
        n=n+1

    data2 = data2[3:]

    data = data + data2

    return(data)


def tropical(ARI, name, year):
    storm_name = name
    storm_year = year


    return_interval = ARI

    import numpy as np
    import matplotlib.pyplot as plt

    import pandas as pd

    df = pd.read_csv("tcr.csv")

    print(df)

    agnes = df[df['Storm']== storm_name + ' ' + storm_year]
    print(storm_name + ' ' + storm_year)

    agnes = agnes.reset_index()

    return(agnes, return_interval, storm_name)

def reports(ARI, name, month, link):
    import requests

    f = requests.get(link)
    print(link)

    QPElist=[]
    lonlist=[]
    latlist=[]
    stationlist=[]


    string=f.text
    string=(string[string.index('**METADATA**'):])

    string=string.split(':')
    for i in string[1:]:
        newstring=i.split(',')

        if '0'+newstring[0][:1]==str(month):
            print(newstring[9])
            if ' RAIN' in newstring[9]:
                stationlist.append((newstring[4]))
                latlist.append(float(newstring[7]))
                lonlist.append(float(newstring[8]))
                QPElist.append(float(newstring[10]))



    return_interval = ARI
    storm_name=name

    import numpy as np
    import matplotlib.pyplot as plt

    import pandas as pd

    #df = pd.read_csv("tcr.csv")
    df = {'Total':QPElist,
        'Lon':lonlist,
        'Lat':latlist,
        'Station':stationlist}

    return(QPElist, lonlist, latlist, stationlist)

def pns(ARI, name, month, linklist):
    return_interval = ARI
    storm_name=name
    QPElist, lonlist, latlist, stationlist = [],[],[],[]

    for link in linklist:
        QPElistinter, lonlistinter, latlistinter, stationlistinter = reports(ARI, name, month, link)
        QPElist = QPElist + (QPElistinter)
        lonlist = lonlist + (lonlistinter)
        latlist = latlist + (latlistinter)
        stationlist= stationlist + (stationlistinter)

    import pandas as pd

    df = {'Total':QPElist,
        'Lon':lonlist,
        'Lat':latlist,
        'Station':stationlist}
    agnes = pd.DataFrame(df)

    print(agnes)

    return(agnes, return_interval, storm_name)


def acis(ARI, name, year, statelist):
    return_interval = ARI
    storm_name= name + ' ' + year
    text_file = open(year + statelist[0]+".txt", "r")

    data = text_file.read()

    #close file
    text_file.close()

    data = data.split("\n")
    n=0
    while n < len(data):
        data[n]=data[n].split(',')
        n=n+1

    data = data[3:]

    if len(statelist)>1:
        for i in statelist[1:]:
            data = add_data(year, i, data)

    if len(data[0])==6:
        l=0
        while l < len(data):
            data[l]=data[l][1:]
            l=l+1


    print(data)

    QPElist=[]
    lonlist=[]
    latlist=[]
    townlist=[]
    import numpy as np

    for i in data:
        if i[2] == ' -' or i[1] == ' -' or i[4] == ' M' or i[4] == ' T':
            latlist.append(np.NaN)
            lonlist.append(np.NaN)
            townlist.append(' ')
            QPElist.append(np.NaN)
        else:
            latlist.append(float(i[2]))
            lonlist.append(float(i[1]))
            QPElist.append(float(i[4]))
            townlist.append(i[0])



    import matplotlib.pyplot as plt

    import pandas as pd

    #df = pd.read_csv("tcr.csv")
    df = {'Total':QPElist,
        'Lon':lonlist,
        'Lat':latlist,
        'Town':townlist}
    agnes = pd.DataFrame(df)

    print(agnes)
    return(agnes, return_interval, storm_name)

def arize(agnes, return_interval, storm_name):
    import requests

    arilist=[]
    z=0

    tl = len(agnes['Lat'])
    print(tl)
    comparisonlist=[1,2,5,10,25,50,100,200,500,1000]
    for i in range(len(agnes['Lat'])):
        z=z+1
        print(str(z) + '/' + str(tl))
        lat = str(agnes['Lat'][i])
        lon = str(agnes['Lon'][i])
        amount = float(agnes['Total'][i])
        if amount > 0.5:
            try:
                link = "https://hdsc.nws.noaa.gov/cgi-bin/hdsc/new/fe_text_mean.csv?lat="+lat+"&lon="+ lon + "&data=depth&units=english&series=pds"
                print(link)
                response = requests.get(link,verify=False)
#                response = requests.get(link)
                content = response.content.decode('latin-1')
                content = content[content.index(return_interval):]
                list = content.split(",")
                list=list[1:11]
                list[9] = list[9][:4]
                n=0
                ari = 0
                for x in list:
                    if amount > float(x):
                        ari = comparisonlist[n]
                    n=n+1
                arilist.append(ari)
            except:
                arilist.append(0)
        else:
            arilist.append(0)

        if z%20 == 0:
            print(arilist)

    print(arilist)
    agnes['ARI'] = arilist
    return(agnes, return_interval, storm_name)



def ariplot(agnes, return_interval, storm_name, year):
    minlat = agnes['Lat'].min()
    minlon = agnes['Lon'].min()
    maxlat = agnes['Lat'].max()
    maxlon = agnes['Lon'].max()

    import matplotlib.pyplot as plt
    import matplotlib
#    fig = plt.figure(figsize=(15, 15))
    import cartopy
    import cartopy.crs as ccrs
    import cartopy.feature as cf
    fig = plt.figure(figsize=(45, 45))

    proj = ccrs.PlateCarree()
    ax1 = fig.add_subplot(1,1,1,projection=proj)
    ax1.set_title(storm_name + " Gridded " + return_interval + " Recurrence Intervals", loc='left', size = 20)
    import cartopy.io.shapereader as shpreader
    import cartopy.feature as cfeature
    import cartopy.crs as ccrs

    fig, ax1 = plt.subplots(subplot_kw={'projection': ccrs.PlateCarree()})

    # Existing borders
    border_resolution = '10m'
    ax1.coastlines(resolution=border_resolution, linewidth=0.8)
    ax1.add_feature(cfeature.STATES.with_scale('10m'), edgecolor=[.3, .3, .3], linewidth=1)
    ax1.add_feature(cfeature.BORDERS.with_scale('10m'), edgecolor=[.3, .3, .3], linewidth=1)

    # Add counties
    shapefile = 'cb_2022_us_county_5m.shp'  # if in same directory
    reader = shpreader.Reader(shapefile)
    counties_feature = cfeature.ShapelyFeature(
        reader.geometries(),
        ccrs.PlateCarree(),
        edgecolor='gray',
        facecolor='none',
        linewidth=0.3
    )
    ax1.add_feature(counties_feature)
    #ax1.set_extent([-100,-90,27,34],crs=ccrs.PlateCarree()) # select region


    # Define the latitude and longitude boundaries of the grid over the United States
    lat_min = minlat - 2
    lat_max = maxlat + 2
    lon_min = minlon - 2
    lon_max = maxlon + 2

    # Define the grid spacing
    grid_spacing = 0.5

    # Create the meshgrid
    lats = np.arange(lat_min, lat_max + grid_spacing, grid_spacing)
    lons = np.arange(lon_min, lon_max + grid_spacing, grid_spacing)
    lon_grid, lat_grid = np.meshgrid(lons, lats)

    # Fill the grid with values as needed
    # For example, let's fill the grid with random values between 0 and 1
    values = np.zeros_like(lon_grid)


    colors = ['white', 'orange','darkorange','red','firebrick','deeppink', 'darkviolet', 'slateblue','blue','darkblue', 'limegreen']
    ARIs = [0, 1,2,5,10,25,50,100,200,500,1000, 10000]

    n=0
    for x in ARIs:
        print(x)
        var = agnes[agnes['ARI']==x]
        var = var.reset_index()

        for i in range(len(var['Lat'])):
            print(n)
            try:
                lat_idx = int((var['Lat'][i] - lat_min) / grid_spacing)
                lon_idx = int((var['Lon'][i] - lon_min) / grid_spacing)
                values[lat_idx, lon_idx] = x
                n = n+1
            except:
                n = n+1

    cmap = matplotlib.colors.ListedColormap(colors)
    cmap.set_under('white')
    cmap.set_over('limegreen')


    num_ones = sum(values)
    num_ones=sum(num_ones)

    bounds = ARIs
    norm = matplotlib.colors.BoundaryNorm(bounds, cmap.N)
    plt.pcolormesh(lon_grid,lat_grid,values,transform=ccrs.PlateCarree(),\
    cmap=cmap,norm=norm)
#    ax1.set_extent([-74.5,-81,39.5,42.5],crs=ccrs.PlateCarree()) # select region
    plt.text(minlon - 2.5, minlat - 4, 'Sum = ' + str(num_ones), fontsize=20, transform=ccrs.PlateCarree(), color='black')
    # Plot the grid
    #plt.pcolormesh(lon_grid, lat_grid, values)
    plt.colorbar(fraction=0.03)
    plt.savefig(storm_name + 'gridARI.png', bbox_inches = 'tight', pad_inches = 0.1)

    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(15, 15))
    import cartopy
    import cartopy.crs as ccrs
    import cartopy.feature as cf
    fig = plt.figure(figsize=(15, 15))

    import matplotlib.lines as mlines  # For custom legend markers


# Previous code for setting up the plot
    proj = ccrs.PlateCarree()
    ax1 = fig.add_subplot(1, 1, 1, projection=proj)
    ax1.set_title(storm_name + " Point " + return_interval + " Recurrence Intervals", loc='left', size=20)
    border_resolution = '10m'  # Adjust the resolution as needed
    ax1.coastlines(resolution=border_resolution, linewidth=0.8)
    ax1.add_feature(cfeature.BORDERS, edgecolor=[.3, .3, .3], linewidth=0.5, linestyle=':')
    ax1.add_feature(cfeature.STATES, edgecolor='gray', linewidth=0.5)

    # Define ARIs and their corresponding colors
    colors = ['bisque', 'orange', 'darkorange', 'red', 'firebrick', 'deeppink', 'darkviolet', 'slateblue', 'blue', 'darkblue', 'limegreen']
    ARIs = [0, 1, 2, 5, 10, 25, 50, 100, 200, 500, 1000]

    # Plot points with colored dots based on ARI values
    n = 0
    for x in ARIs:
        print(x)
        var = agnes[agnes['ARI'] == x]
        var = var.reset_index()
        for i in range(len(var['Lat'])):
            plt.plot(var['Lon'][i], var['Lat'][i], color=colors[n], linewidth=0.5, marker='o', transform=ccrs.Geodetic())
        n = n + 1

    # Create a list of custom legend markers for each ARI
    legend_markers = [mlines.Line2D([], [], color=color, marker='o', linestyle='None', markersize=8, label=f'{ari} year')
                      for color, ari in zip(colors, ARIs)]

    # Add legend to the plot, positioning it outside the plot area (right side)
    plt.legend(handles=legend_markers, title="ARI", loc='center left', fontsize=12, title_fontsize='13',
               bbox_to_anchor=(1.05, 0.5), borderaxespad=0.)

    # Adjust the layout to make room for the legend
    plt.subplots_adjust(right=0.75)

    # Save the plot
    agnes.to_csv(storm_name + str(year) + 'ari.csv')
    plt.savefig(storm_name + 'ARI.png', bbox_inches='tight', pad_inches=0.1)


def ariplot_old(agnes, return_interval, storm_name, year):
    minlat = agnes['Lat'].min()
    minlon = agnes['Lon'].min()
    maxlat = agnes['Lat'].max()
    maxlon = agnes['Lon'].max()

    import matplotlib.pyplot as plt
    import matplotlib
#    fig = plt.figure(figsize=(15, 15))
    import cartopy
    import cartopy.crs as ccrs
    import cartopy.feature as cf
    fig = plt.figure(figsize=(15, 15))

    proj = ccrs.PlateCarree()
    ax1 = fig.add_subplot(1,1,1,projection=proj)
    ax1.set_title(storm_name + " Gridded " + return_interval + " Recurrence Intervals", loc='left', size = 20)
    border_resolution = '10m'  # Adjust the resolution as needed
    ax1.coastlines(resolution=border_resolution, linewidth=0.8)
    ax1.add_feature(cfeature.BORDERS, edgecolor=[.3, .3, .3], linewidth=0.5, linestyle=':')
    ax1.add_feature(cfeature.STATES, edgecolor='gray', linewidth=0.5)
    #ax1.set_extent([-100,-90,27,34],crs=ccrs.PlateCarree()) # select region


    # Define the latitude and longitude boundaries of the grid over the United States
    lat_min = minlat - 2
    lat_max = maxlat + 2
    lon_min = minlon - 2
    lon_max = maxlon + 2

    # Define the grid spacing
    grid_spacing = 0.5

    # Create the meshgrid
    lats = np.arange(lat_min, lat_max + grid_spacing, grid_spacing)
    lons = np.arange(lon_min, lon_max + grid_spacing, grid_spacing)
    lon_grid, lat_grid = np.meshgrid(lons, lats)

    # Fill the grid with values as needed
    # For example, let's fill the grid with random values between 0 and 1
    values = np.zeros_like(lon_grid)


    colors = ['orange','darkorange','red','firebrick','deeppink', 'darkviolet', 'slateblue','blue','darkblue']
    ARIs = [1,2,5,10,25,50,100,200,500,1000]

    n=0
    for x in ARIs:
        print(x)
        var = agnes[agnes['ARI']==x]
        var = var.reset_index()

        for i in range(len(var['Lat'])):
            print(n)
            try:
                lat_idx = int((var['Lat'][i] - lat_min) / grid_spacing)
                lon_idx = int((var['Lon'][i] - lon_min) / grid_spacing)
                values[lat_idx, lon_idx] = x
                n = n+1
            except:
                n = n+1

    cmap = matplotlib.colors.ListedColormap(colors)
    cmap.set_under('white')
    cmap.set_over('limegreen')


    num_ones = sum(values)
    num_ones=sum(num_ones)

    bounds = ARIs
    norm = matplotlib.colors.BoundaryNorm(bounds, cmap.N)
    plt.pcolormesh(lon_grid,lat_grid,values,transform=ccrs.PlateCarree(),\
    cmap=cmap,norm=norm)
#    ax1.set_extent([-74.5,-81,39.5,42.5],crs=ccrs.PlateCarree()) # select region
    plt.text(minlon - 2.5, minlat - 4, 'Sum = ' + str(num_ones), fontsize=20, transform=ccrs.PlateCarree(), color='black')
    # Plot the grid
    #plt.pcolormesh(lon_grid, lat_grid, values)
    plt.colorbar(fraction=0.03)
    plt.savefig(storm_name + 'gridARI.png', bbox_inches = 'tight', pad_inches = 0.1)

    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(15, 15))
    import cartopy
    import cartopy.crs as ccrs
    import cartopy.feature as cf
    fig = plt.figure(figsize=(15, 15))

    proj = ccrs.PlateCarree()
    ax1 = fig.add_subplot(1,1,1,projection=proj)
    ax1.set_title(storm_name + " Point " + return_interval + " Recurrence Intervals", loc='left', size = 20)
    border_resolution = '10m'  # Adjust the resolution as needed
    ax1.coastlines(resolution=border_resolution, linewidth=0.8)
    ax1.add_feature(cfeature.BORDERS, edgecolor=[.3, .3, .3], linewidth=0.5, linestyle=':')
    ax1.add_feature(cfeature.STATES, edgecolor='gray', linewidth=0.5)
    #ax1.set_extent([-82,-78,24,28],crs=ccrs.PlateCarree()) # select region


    colors = ['bisque','orange','darkorange','red','firebrick','deeppink', 'darkviolet', 'slateblue', 'blue','darkblue','limegreen']
    ARIs = [0,1,2,5,10,25,50,100,200,500,1000]

    n=0
    for x in ARIs:
        print(x)
        var = agnes[agnes['ARI']==x]
        var = var.reset_index()
        for i in range(len(var['Lat'])):
            plt.plot(var['Lon'][i], var['Lat'][i], color=colors[n], linewidth=0.5, marker='o', transform=ccrs.Geodetic())
        n = n+1

    agnes.to_csv(storm_name + str(year) +  'ari.csv')

    plt.savefig(storm_name + 'ARI.png', bbox_inches = 'tight', pad_inches = 0.1)


def totalplot(agnes, return_interval, storm_name):
    minlat = agnes['Lat'].min()
    minlon = agnes['Lon'].min()
    maxlat = agnes['Lat'].max()
    maxlon = agnes['Lon'].max()


    import matplotlib.pyplot as plt
    import matplotlib
#    fig = plt.figure(figsize=(15, 15))
    import cartopy
    import cartopy.crs as ccrs
    import cartopy.feature as cf
    fig = plt.figure(figsize=(15, 15))

    proj = ccrs.PlateCarree()
    ax1 = fig.add_subplot(1,1,1,projection=proj)
    ax1.set_title(storm_name + " Gridded " + return_interval + " Total Precipitation (Inches)", loc='left', size = 20)
    border_resolution = '10m'  # Adjust the resolution as needed
    ax1.coastlines(resolution=border_resolution, linewidth=0.8)
    ax1.add_feature(cfeature.BORDERS, edgecolor=[.3, .3, .3], linewidth=0.5, linestyle=':')
    ax1.add_feature(cfeature.STATES, edgecolor='gray', linewidth=0.5)
    ax1.set_extent([-74,-84,36.5,39.5],crs=ccrs.PlateCarree()) # select region # select region



    # Define the latitude and longitude boundaries of the grid over the United States
    lat_min = minlat - 2
    lat_max = maxlat + 2
    lon_min = minlon - 2
    lon_max = maxlon + 2

    # Define the grid spacing
    grid_spacing = 0.3

    # Create the meshgrid
    lats = np.arange(lat_min, lat_max + grid_spacing, grid_spacing)
    lons = np.arange(lon_min, lon_max + grid_spacing, grid_spacing)
    lon_grid, lat_grid = np.meshgrid(lons, lats)

    # Fill the grid with values as needed
    # For example, let's fill the grid with random values between 0 and 1
    values = np.zeros_like(lon_grid)


    colors = ([('white'),(122/255, 244/255, 64/255),(97/255, 207/255, 52/255),(63/255, 140/255, 33/255),(18/255, 78/255, 139/255),(42/255, 143/255, 247/255),(68/255, 179/255, 238/255),(104/255, 239/255, 238/255),(138/255, 104/255, 205/255),(147/255, 74/255, 238/255),(140/255, 48/255, 140/255),(140/255, 29/255, 25/255),(206/255, 48/255, 43/255),(237/255, 65/255, 52/255),(241/255, 126/255, 58/255),(205/255, 134/255, 52/255),(252/255, 216/255, 74/255),(238/255, 239/255, 77/255),(244/255, 173/255, 184/255)])
    ARIs = [0,0.01,0.1,0.25,0.5,0.75,1,1.25,1.5,1.75,2,2.5,3,4,5,7,10,15,20,100]

    n=0
    for x in ARIs:
        print(x)
        var = agnes[agnes['Total']>x]
        var = var.reset_index()

        for i in range(len(var['Lat'])):
            print(n)
            try:
                lat_idx = int((var['Lat'][i] - lat_min) / grid_spacing)
                lon_idx = int((var['Lon'][i] - lon_min) / grid_spacing)
                values[lat_idx, lon_idx] = x
                n = n+1
            except:
                n = n+1

#    agnes.to_csv(storm_name + 'precip.csv')

    cmap = matplotlib.colors.ListedColormap(colors)
#    cmap.set_under('white')
#    cmap.set_over('limegreen')


    num_ones = sum(values)
    num_ones=sum(num_ones)

    bounds = ARIs
    norm = matplotlib.colors.BoundaryNorm(bounds, cmap.N)

    plt.pcolormesh(lon_grid,lat_grid,values,transform=ccrs.PlateCarree(),\
    cmap=cmap,norm=norm)
#    ax1.set_extent([-74.5,-81,39.5,42.5],crs=ccrs.PlateCarree()) # select region # select region

    #plt.text(minlon - 2.5, minlat - 4, 'Sum = ' + str(num_ones), fontsize=20, transform=ccrs.PlateCarree(), color='black')
    # Plot the grid
    #plt.pcolormesh(lon_grid, lat_grid, values)
    plt.colorbar(fraction=0.02)

    plt.savefig(storm_name + 'gridtotals.png', bbox_inches = 'tight', pad_inches = 0.1)


def ariplotinterp(agnes, return_interval, storm_name):
        agnes = agnes.dropna()
        minlat = agnes['Lat'].min()
        minlon = agnes['Lon'].min()
        maxlat = agnes['Lat'].max()
        maxlon = agnes['Lon'].max()


        import matplotlib.pyplot as plt
        import matplotlib
    #    fig = plt.figure(figsize=(15, 15))
        import cartopy
        import cartopy.crs as ccrs
        import cartopy.feature as cf
        fig = plt.figure(figsize=(15, 15))

        proj = ccrs.PlateCarree()
        ax1 = fig.add_subplot(1,1,1,projection=proj)
        ax1.set_title(storm_name +" "+ return_interval + " Average Recurrence Intervals", loc='left', size = 20)
        border_resolution = '10m'  # Adjust the resolution as needed
        ax1.coastlines(resolution=border_resolution, linewidth=0.8)
        ax1.add_feature(cfeature.BORDERS, edgecolor=[.3, .3, .3], linewidth=0.5, linestyle=':')
        ax1.add_feature(cfeature.STATES, edgecolor='gray', linewidth=0.5)

        import pandas as pd
        import numpy as np
        import matplotlib.pyplot as plt
        from scipy.interpolate import griddata


        # Define the grid for interpolation (latitude and longitude ranges)
        latitude_grid = np.linspace(agnes['Lat'].min(), agnes['Lat'].max(), 100)
        longitude_grid = np.linspace(agnes['Lon'].min(), agnes['Lon'].max(), 100)


        # Create a meshgrid for latitude and longitude
        latitude_mesh, longitude_mesh = np.meshgrid(latitude_grid, longitude_grid)

        # Perform linear interpolation using griddata
        interpolated_precip = griddata(
            (agnes['Lat'], agnes['Lon']), agnes['ARI']*1.5,
            (latitude_mesh, longitude_mesh),
            method='linear'
        )

        colors = ['orange','darkorange','red','firebrick','deeppink', 'darkviolet', 'slateblue','blue','darkblue']
        ARIs = [1,2,5,10,25,50,100,200,500,1000]

        cmap = matplotlib.colors.ListedColormap(colors)
        cmap.set_over('limegreen')
        cmap.set_under('white')


        bounds = ARIs
        norm = matplotlib.colors.BoundaryNorm(bounds, cmap.N)



        # Create a contour plot
        plt.contourf(longitude_mesh, latitude_mesh, interpolated_precip, transform=ccrs.PlateCarree(),\
        cmap=cmap,norm=norm,levels=bounds, ticks=bounds, extend='both')
#        plt.colorbar(label='Precipitation')


    #    ax1.set_extent([-74.5,-81,39.5,42.5],crs=ccrs.PlateCarree()) # select region # select region

#        plt.text(minlon - 2.5, minlat - 4, 'Sum = ' + str(num_ones), fontsize=20, transform=ccrs.PlateCarree(), color='black')
        # Plot the grid
        #plt.pcolormesh(lon_grid, lat_grid, values)
        plt.colorbar(fraction=0.03)

        plt.savefig(storm_name + 'interpari.png', bbox_inches = 'tight', pad_inches = 0.1)



def totalplotinterp(agnes, return_interval, storm_name):
        agnes = agnes.dropna()
        minlat = agnes['Lat'].min()
        minlon = agnes['Lon'].min()
        maxlat = agnes['Lat'].max()
        maxlon = agnes['Lon'].max()


        import matplotlib.pyplot as plt
        import matplotlib
    #    fig = plt.figure(figsize=(15, 15))
        import cartopy
        import cartopy.crs as ccrs
        import cartopy.feature as cf
        fig = plt.figure(figsize=(15, 15))

        proj = ccrs.PlateCarree()
        ax1 = fig.add_subplot(1,1,1,projection=proj)
        ax1.set_title(storm_name +" "+return_interval + " Total Precipitation (Inches)", loc='left', size = 20)
        border_resolution = '10m'  # Adjust the resolution as needed
        ax1.coastlines(resolution=border_resolution, linewidth=0.8)
        ax1.add_feature(cfeature.BORDERS, edgecolor=[.3, .3, .3], linewidth=0.5, linestyle=':')
        ax1.add_feature(cfeature.STATES, edgecolor='gray', linewidth=0.5)

        import pandas as pd
        import numpy as np
        import matplotlib.pyplot as plt
        from scipy.interpolate import griddata


        # Define the grid for interpolation (latitude and longitude ranges)
        latitude_grid = np.linspace(agnes['Lat'].min(), agnes['Lat'].max(), 100)
        longitude_grid = np.linspace(agnes['Lon'].min(), agnes['Lon'].max(), 100)


        # Create a meshgrid for latitude and longitude
        latitude_mesh, longitude_mesh = np.meshgrid(latitude_grid, longitude_grid)

        # Perform linear interpolation using griddata
        interpolated_precip = griddata(
            (agnes['Lat'], agnes['Lon']), agnes['Total'],
            (latitude_mesh, longitude_mesh),
            method='linear'
        )

        colors = ([('white'),(122/255, 244/255, 64/255),(97/255, 207/255, 52/255),(63/255, 140/255, 33/255),(18/255, 78/255, 139/255),(42/255, 143/255, 247/255),(68/255, 179/255, 238/255),(104/255, 239/255, 238/255),(138/255, 104/255, 205/255),(147/255, 74/255, 238/255),(140/255, 48/255, 140/255),(140/255, 29/255, 25/255),(206/255, 48/255, 43/255),(237/255, 65/255, 52/255),(241/255, 126/255, 58/255),(205/255, 134/255, 52/255),(252/255, 216/255, 74/255),(238/255, 239/255, 77/255),(244/255, 173/255, 184/255)])
        ARIs = [0,0.01,0.1,0.25,0.5,0.75,1,1.25,1.5,1.75,2,2.5,3,4,5,7,10,15,20,100]

        cmap = matplotlib.colors.ListedColormap(colors)


        bounds = ARIs
        norm = matplotlib.colors.BoundaryNorm(bounds, cmap.N)



        # Create a contour plot
        plt.contourf(longitude_mesh, latitude_mesh, interpolated_precip, transform=ccrs.PlateCarree(),\
        cmap=cmap,norm=norm,levels=bounds, ticks=bounds, extend='both')
#        plt.colorbar(label='Precipitation')


    #    ax1.set_extent([-74.5,-81,39.5,42.5],crs=ccrs.PlateCarree()) # select region # select region

#        plt.text(minlon - 2.5, minlat - 4, 'Sum = ' + str(num_ones), fontsize=20, transform=ccrs.PlateCarree(), color='black')
        # Plot the grid
        #plt.pcolormesh(lon_grid, lat_grid, values)
        plt.colorbar(fraction=0.03)

        ax1.add_feature(cf.OCEAN, zorder=100, edgecolor='k')

        plt.savefig(storm_name + 'interptotals.png', bbox_inches = 'tight', pad_inches = 0.1)




def kize(agnes, return_interval, storm_name):
    import requests

    klist=[]
    krawlist=[]
    z=0
    comparisonlist= [0,25,50,75,90,95,100,105,110,125,150]
    for i in range(len(agnes['Lat'])):
        z=z+1
        print(z)
        lat = str(agnes['Lat'][i])
        lon = str(agnes['Lon'][i])
        amount = float(agnes['Total'][i])
        if amount > 2:
            try:
                link = "https://hdsc.nws.noaa.gov/cgi-bin/hdsc/new/fe_text_mean.csv?lat="+lat+"&lon="+ lon + "&data=depth&units=english&series=pds"
                print(link)
                response = requests.get(link,verify=False)
#                response = requests.get(link)
                content = response.content.decode('latin-1')
                content = content[content.index(return_interval):]
                list = content.split(",")
                list=list[1:11]
                list[9] = list[9][:4]
#                print('start')
                n=0
                ari = 0
                kamt = list[9]
                ratio = (amount/float(kamt)) * 100
                krawlist.append(ratio)
                for x in comparisonlist:
                    if ratio > x:
                        kratio = x

                klist.append(kratio)
            except:
                klist.append(0)
                krawlist.append(0)
        else:
            klist.append(0)
            krawlist.append(0)


        if z%20 == 0:
            print(klist)
            print(krawlist)

    print(klist)
    print(krawlist)
    agnes['Ktier'] = klist
    agnes['Kraw'] = krawlist
    return(agnes, return_interval, storm_name)

def kplot(agnes, return_interval, storm_name):

    minlat = agnes['Lat'].min()
    minlon = agnes['Lon'].min()
    maxlat = agnes['Lat'].max()
    maxlon = agnes['Lon'].max()

    import matplotlib.pyplot as plt
    import matplotlib
#    fig = plt.figure(figsize=(15, 15))
    import cartopy
    import cartopy.crs as ccrs
    import cartopy.feature as cf
    fig = plt.figure(figsize=(15, 15))

    proj = ccrs.PlateCarree()
    ax1 = fig.add_subplot(1,1,1,projection=proj)
    ax1.set_title(storm_name + " Gridded " + return_interval + " % of 1000-year ARI", loc='left', size = 20)
    border_resolution = '10m'  # Adjust the resolution as needed
    ax1.coastlines(resolution=border_resolution, linewidth=0.8)
    ax1.add_feature(cfeature.BORDERS, edgecolor=[.3, .3, .3], linewidth=0.5, linestyle=':')
    ax1.add_feature(cfeature.STATES, edgecolor='gray', linewidth=0.5)
    #ax1.set_extent([-100,-90,27,34],crs=ccrs.PlateCarree()) # select region


    # Define the latitude and longitude boundaries of the grid over the United States
    lat_min = minlat - 2
    lat_max = maxlat + 2
    lon_min = minlon - 2
    lon_max = maxlon + 2

    # Define the grid spacing
    grid_spacing = 0.5

    # Create the meshgrid
    lats = np.arange(lat_min, lat_max + grid_spacing, grid_spacing)
    lons = np.arange(lon_min, lon_max + grid_spacing, grid_spacing)
    lon_grid, lat_grid = np.meshgrid(lons, lats)

    # Fill the grid with values as needed
    # For example, let's fill the grid with random values between 0 and 1
    values = np.zeros_like(lon_grid)


    colors = ['white','bisque','orange','darkorange','red','firebrick','deeppink', 'darkviolet', 'slateblue', 'blue','darkblue','limegreen']
    kbands = [0,25,50,75,90,95,100,105,110,125,150]

    n=0
    for x in kbands:
        print(x)
        var = agnes[agnes['Ktier']==x]
        var = var.reset_index()

        for i in range(len(var['Lat'])):
            print(n)
            try:
                lat_idx = int((var['Lat'][i] - lat_min) / grid_spacing)
                lon_idx = int((var['Lon'][i] - lon_min) / grid_spacing)
                values[lat_idx, lon_idx] = x
                n = n+1
            except:
                n = n+1

    cmap = matplotlib.colors.ListedColormap(colors)
    cmap.set_under('white')
    cmap.set_over('limegreen')


    num_ones = sum(values)
    num_ones=sum(num_ones)

    bounds = kbands
    norm = matplotlib.colors.BoundaryNorm(bounds, cmap.N)
    plt.pcolormesh(lon_grid,lat_grid,values,transform=ccrs.PlateCarree(),\
    cmap=cmap,norm=norm)
#    ax1.set_extent([-74.5,-81,39.5,42.5],crs=ccrs.PlateCarree()) # select region
    plt.text(minlon - 2.5, minlat - 4, 'Sum = ' + str(num_ones), fontsize=20, transform=ccrs.PlateCarree(), color='black')
    # Plot the grid
    #plt.pcolormesh(lon_grid, lat_grid, values)
    plt.colorbar(fraction=0.02)
    plt.savefig(storm_name + 'gridkARI.png', bbox_inches = 'tight', pad_inches = 0.1)

    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(15, 15))
    import cartopy
    import cartopy.crs as ccrs
    import cartopy.feature as cf
    fig = plt.figure(figsize=(15, 15))

    proj = ccrs.PlateCarree()
    ax1 = fig.add_subplot(1,1,1,projection=proj)
    ax1.set_title(storm_name + " Point " + return_interval + " % of 1000-year ARI", loc='left', size = 20)
    border_resolution = '10m'  # Adjust the resolution as needed
    ax1.coastlines(resolution=border_resolution, linewidth=0.8)
    ax1.add_feature(cfeature.BORDERS, edgecolor=[.3, .3, .3], linewidth=0.5, linestyle=':')
    ax1.add_feature(cfeature.STATES, edgecolor='gray', linewidth=0.5)
    #ax1.set_extent([-82,-78,24,28],crs=ccrs.PlateCarree()) # select region

    agnes.plot(x="Lon", y="Lat", kind="scatter", c="Kraw",
        colormap="summer", ax=ax1)

#    cbar = ax1.collections[0].colorbar

#    cbar.ax.fraction(0.02)


    plt.savefig(storm_name + 'kARI.png', bbox_inches = 'tight', pad_inches = 0.1)

def totalplotinterpcrest(agnes, return_interval, storm_name, monthyear):
        agnes = agnes.dropna()
        minlat = agnes['Lat'].min()
        minlon = agnes['Lon'].min()
        maxlat = agnes['Lat'].max()
        maxlon = agnes['Lon'].max()


        import matplotlib.pyplot as plt
        import matplotlib
    #    fig = plt.figure(figsize=(15, 15))
        import cartopy
        import cartopy.crs as ccrs
        import cartopy.feature as cf
        fig = plt.figure(figsize=(45, 45))

        proj = ccrs.PlateCarree()
        ax1 = fig.add_subplot(1,1,1,projection=proj)
        ax1.set_title(storm_name +" "+return_interval + " Total Precipitation (Inches)", loc='left', size = 20)

        import cartopy.io.shapereader as shpreader
        import cartopy.feature as cfeature
        import cartopy.crs as ccrs

        fig, ax1 = plt.subplots(subplot_kw={'projection': ccrs.PlateCarree()})

        # Existing borders
        border_resolution = '10m'
        ax1.coastlines(resolution=border_resolution, linewidth=0.8)
        ax1.add_feature(cfeature.STATES.with_scale('10m'), edgecolor=[.3, .3, .3], linewidth=1)
        ax1.add_feature(cfeature.BORDERS.with_scale('10m'), edgecolor=[.3, .3, .3], linewidth=1)

        # Add counties
        shapefile = 'cb_2022_us_county_5m.shp'  # if in same directory
        reader = shpreader.Reader(shapefile)
        counties_feature = cfeature.ShapelyFeature(
            reader.geometries(),
            ccrs.PlateCarree(),
            edgecolor='gray',
            facecolor='none',
            linewidth=0.3
        )
        ax1.add_feature(counties_feature)

#        ax1.gridlines(draw_labels=True, linewidth=1, color='black', alpha=0.5, linestyle='--')



#        ax1.add_feature(cfeature.STATES, edgecolor='gray', linewidth=0.5)

        import pandas as pd
        import numpy as np
        import matplotlib.pyplot as plt
        from scipy.interpolate import griddata


        # Define the grid for interpolation (latitude and longitude ranges)
        latitude_grid = np.linspace(agnes['Lat'].min(), agnes['Lat'].max(), 100)
        longitude_grid = np.linspace(agnes['Lon'].min(), agnes['Lon'].max(), 100)


        # Create a meshgrid for latitude and longitude
        latitude_mesh, longitude_mesh = np.meshgrid(latitude_grid, longitude_grid)

        # Perform linear interpolation using griddata
        interpolated_precip = griddata(
            (agnes['Lat'], agnes['Lon']), agnes['Total'],
            (latitude_mesh, longitude_mesh),
            method='linear'
        )

        colors = ([('white'),(122/255, 244/255, 64/255),(97/255, 207/255, 52/255),(63/255, 140/255, 33/255),(18/255, 78/255, 139/255),(42/255, 143/255, 247/255),(68/255, 179/255, 238/255),(104/255, 239/255, 238/255),(138/255, 104/255, 205/255),(147/255, 74/255, 238/255),(140/255, 48/255, 140/255),(140/255, 29/255, 25/255),(206/255, 48/255, 43/255),(237/255, 65/255, 52/255),(241/255, 126/255, 58/255),(205/255, 134/255, 52/255),(252/255, 216/255, 74/255),(238/255, 239/255, 77/255),(244/255, 173/255, 184/255)])
        ARIs = [0,0.01,0.1,0.25,0.5,0.75,1,1.25,1.5,1.75,2,2.5,3,4,5,7,10,15,20,100]

        cmap = matplotlib.colors.ListedColormap(colors)


        bounds = ARIs
        norm = matplotlib.colors.BoundaryNorm(bounds, cmap.N)



        # Create a contour plot
        plt.contourf(longitude_mesh, latitude_mesh, interpolated_precip, transform=ccrs.PlateCarree(),\
        cmap=cmap,norm=norm,levels=bounds, ticks=bounds, extend='both')
#        plt.colorbar(label='Precipitation')

#        plt.text(minlon - 2.5, minlat - 4, 'Sum = ' + str(num_ones), fontsize=20, transform=ccrs.PlateCarree(), color='black')
        # Plot the grid
        #plt.pcolormesh(lon_grid, lat_grid, values)
        plt.colorbar(fraction=0.03)


        import marfc_list as ma
        import pandas as pd
        import matplotlib.pyplot as plt
        import matplotlib
        import numpy as np

        from IPython.display import HTML


        #bigtext = ma.olist() + ma.rlist() + ma.clist() + ma.alist() + ma.mblist() + ma.wlist() + ma.slist()
        bigtext = open("nationalrivers.txt", "r")
        bigtext = (bigtext.read())
        import ast
        bigtext = ast.literal_eval(bigtext)

        Title = []
        Latitude=[]
        Longitude = []
        Location = []
        Rankings = []
        One = []
        for i in bigtext:
            Title.append(i[0])
            Latitude.append(float(i[1][0]))
            Longitude.append(float(i[1][1]))
            Location.append(i[1])
            Rankings.append(i[2])

        df = {'Title':Title,
            'Location':Location,
            'Latitude':Latitude,
            'Longitude':Longitude,
            'Rankings':Rankings}
        df = pd.DataFrame(df)
        print(minlon)
        print(df['Longitude'][0])

        df = df[df['Latitude']>minlat]
        df = df[df['Latitude']<maxlat]
        df = df[df['Longitude']>(-1*maxlon)]
        df = df[df['Longitude']<(-1*minlon)]
        df=df.reset_index()

        One = []
        Two = []
        Three = []

        for i in df['Rankings']:
            oneb = i.index('(1)')+4
            i = i[oneb:]
            oneb = i.index('on') + 3
            onee = i.index('<b')
            one = i[oneb:onee]
            One.append(one)

            twob = i.index('(2)')+4
            i = i[twob:]
            twob = i.index('on') + 3
            twoe = i.index('<b')
            two = i[twob:twoe]
            Two.append(two)

            try:
                threeb = i.index('(3)')+4
                i = i[threeb:]
                threeb = i.index('on') + 3
                threee = i.index('<b')
                three = i[threeb:threee]
                Three.append(three)
            except:
                Three.append('01/01/1900')
        df['OneD'] = One
        df['TwoD'] = Two
        df['ThreeD'] = Three



        MY = []
        yearl = []
        months=[]
        for i in df['OneD']:
            month = i[:2]
            year = i[6:10]
            yearl.append(int(year))
            months.append(int(year[:3]))
            MY.append(month + '/' + year)

        df['MY'] = MY
        df['month'] = months
        df['year'] = yearl

        MY2 = []
        yearl2=[]
        for i in df['TwoD']:
            month = i[:2]
            year = i[6:10]
            yearl2.append(year)
            MY2.append(month + '/' + year)

        df['MY2'] = MY2
        df['year2'] = yearl2

        MY3 = []
        yearl3=[]
        for i in df['ThreeD']:
            month = i[:2]
            year = i[6:10]
            yearl3.append(year)
            MY3.append(month + '/' + year)

        df['MY3'] = MY3
        df['year3'] = yearl3

        June1972 = df[df['MY']==monthyear]

        for i in June1972['Location']:
            plt.plot(-float(i[1]), float(i[0]), color='black', linewidth=3, marker='s', transform=ccrs.Geodetic())

        ax1.add_feature(cfeature.OCEAN.with_scale('10m'), zorder=100, edgecolor='lightblue', facecolor='lightblue', linewidth=0.5)  # High-resolution ocean border
        ax1.add_feature(cfeature.LAKES.with_scale('10m'), zorder=100, edgecolor='lightblue', facecolor='lightblue', linewidth=0.5)  # High-resolution ocean border

        plt.savefig(storm_name + 'interpcresttotals.png', bbox_inches = 'tight', pad_inches = 0.1)




def ariplotinterpcrest(agnes, return_interval, storm_name, monthyear):
        agnes = agnes.dropna()
        minlat = agnes['Lat'].min()
        minlon = agnes['Lon'].min()
        maxlat = agnes['Lat'].max()
        maxlon = agnes['Lon'].max()
        import pyproj



        import matplotlib.pyplot as plt
        import matplotlib
    #    fig = plt.figure(figsize=(15, 15))
        import cartopy
        import cartopy.crs as ccrs
        import cartopy.feature as cf
        fig = plt.figure(figsize=(15, 15))

        proj = ccrs.PlateCarree()

        ax1 = fig.add_subplot(1,1,1,projection=proj)
        ax1.set_title(storm_name +" "+return_interval + " ARIs", loc='left', size = 20)

        import cartopy.io.shapereader as shpreader
        import cartopy.feature as cfeature
        import cartopy.crs as ccrs

        fig, ax1 = plt.subplots(subplot_kw={'projection': ccrs.PlateCarree()})

        # Existing borders
        border_resolution = '10m'
        ax1.coastlines(resolution=border_resolution, linewidth=0.8)
        ax1.add_feature(cfeature.STATES.with_scale('10m'), edgecolor=[.3, .3, .3], linewidth=1)
        ax1.add_feature(cfeature.BORDERS.with_scale('10m'), edgecolor=[.3, .3, .3], linewidth=1)

        # Add counties
        shapefile = 'cb_2022_us_county_5m.shp'  # if in same directory
        reader = shpreader.Reader(shapefile)
        counties_feature = cfeature.ShapelyFeature(
            reader.geometries(),
            ccrs.PlateCarree(),
            edgecolor='gray',
            facecolor='none',
            linewidth=0.3
        )
        ax1.add_feature(counties_feature)
#        ax1.add_feature(cfeature.STATES, edgecolor='gray', linewidth=0.5)

        import pandas as pd
        import numpy as np
        import matplotlib.pyplot as plt
        from scipy.interpolate import griddata


        # Define the grid for interpolation (latitude and longitude ranges)
        latitude_grid = np.linspace(agnes['Lat'].min(), agnes['Lat'].max(), 50)
        longitude_grid = np.linspace(agnes['Lon'].min(), agnes['Lon'].max(), 50)


        # Create a meshgrid for latitude and longitude
        latitude_mesh, longitude_mesh = np.meshgrid(latitude_grid, longitude_grid)

        # Perform linear interpolation using griddata
        interpolated_precip = griddata(
            (agnes['Lat'], agnes['Lon']), agnes['ARI']*1.5,
            (latitude_mesh, longitude_mesh),
            method='linear'
        )

        colors = ['orange','darkorange','red','firebrick','deeppink', 'darkviolet', 'slateblue','blue','darkblue']
        ARIs = [1,2,5,10,25,50,100,200,500,1000]

        cmap = matplotlib.colors.ListedColormap(colors)

#                cmap = matplotlib.colors.ListedColormap(colors)
        cmap.set_over('limegreen')
        cmap.set_under('white')



        bounds = ARIs
        norm = matplotlib.colors.BoundaryNorm(bounds, cmap.N)



        # Create a contour plot
        plt.contourf(longitude_mesh, latitude_mesh, interpolated_precip, transform=ccrs.PlateCarree(),\
        cmap=cmap,norm=norm,levels=bounds, ticks=bounds, extend='both')
#        plt.colorbar(label='Precipitation')


    #    ax1.set_extent([-74.5,-81,39.5,42.5],crs=ccrs.PlateCarree()) # select region # select region

#        plt.text(minlon - 2.5, minlat - 4, 'Sum = ' + str(num_ones), fontsize=20, transform=ccrs.PlateCarree(), color='black')
        # Plot the grid
        #plt.pcolormesh(lon_grid, lat_grid, values)
        plt.colorbar(fraction=0.03)


        import marfc_list as ma
        import pandas as pd
        import matplotlib.pyplot as plt
        import matplotlib
        import numpy as np

        from IPython.display import HTML


        #bigtext = ma.olist() + ma.rlist() + ma.clist() + ma.alist() + ma.mblist() + ma.wlist() + ma.slist()
        bigtext = open("nationalrivers.txt", "r")
        bigtext = (bigtext.read())
        import ast
        bigtext = ast.literal_eval(bigtext)

        Title = []
        Latitude=[]
        Longitude = []
        Location = []
        Rankings = []
        One = []
        for i in bigtext:
            Title.append(i[0])
            Latitude.append(float(i[1][0]))
            Longitude.append(float(i[1][1]))
            Location.append(i[1])
            Rankings.append(i[2])

        df = {'Title':Title,
            'Location':Location,
            'Latitude':Latitude,
            'Longitude':Longitude,
            'Rankings':Rankings}
        df = pd.DataFrame(df)
        print(minlon)
        print(df['Longitude'][0])

        df = df[df['Latitude']>minlat]
        df = df[df['Latitude']<maxlat]
        df = df[df['Longitude']>(-1*maxlon)]
        df = df[df['Longitude']<(-1*minlon)]
        df=df.reset_index()

        One = []
        Two = []
        Three = []

        for i in df['Rankings']:
            oneb = i.index('(1)')+4
            i = i[oneb:]
            oneb = i.index('on') + 3
            onee = i.index('<b')
            one = i[oneb:onee]
            One.append(one)

            twob = i.index('(2)')+4
            i = i[twob:]
            twob = i.index('on') + 3
            twoe = i.index('<b')
            two = i[twob:twoe]
            Two.append(two)

            try:
                threeb = i.index('(3)')+4
                i = i[threeb:]
                threeb = i.index('on') + 3
                threee = i.index('<b')
                three = i[threeb:threee]
                Three.append(three)
            except:
                Three.append('01/01/1900')
        df['OneD'] = One
        df['TwoD'] = Two
        df['ThreeD'] = Three



        MY = []
        yearl = []
        months=[]
        for i in df['OneD']:
            month = i[:2]
            year = i[6:10]
            yearl.append(int(year))
            months.append(int(year[:3]))
            MY.append(month + '/' + year)

        df['MY'] = MY
        df['month'] = months
        df['year'] = yearl

        MY2 = []
        yearl2=[]
        for i in df['TwoD']:
            month = i[:2]
            year = i[6:10]
            yearl2.append(year)
            MY2.append(month + '/' + year)

        df['MY2'] = MY2
        df['year2'] = yearl2

        MY3 = []
        yearl3=[]
        for i in df['ThreeD']:
            month = i[:2]
            year = i[6:10]
            yearl3.append(year)
            MY3.append(month + '/' + year)

        df['MY3'] = MY3
        df['year3'] = yearl3

        June1972 = df[df['MY']==monthyear]

        for i in June1972['Location']:
            plt.plot(-float(i[1]), float(i[0]), color='yellow', linewidth=3, marker='s', transform=ccrs.Geodetic())

        ax1.add_feature(cfeature.OCEAN.with_scale('10m'), zorder=100, edgecolor='lightblue', facecolor='lightblue', linewidth=0.5)  # High-resolution ocean border
        ax1.add_feature(cfeature.LAKES.with_scale('10m'), zorder=100, edgecolor='lightblue', facecolor='lightblue', linewidth=0.5)  # High-resolution ocean border


#        plt.text(-120, 31, '3rd crest (n = ' + str(len(June1972)) + ')', fontsize=20, transform=ccrs.PlateCarree(), color='red')
        plt.savefig(storm_name + 'interparicrest.png', bbox_inches = 'tight', pad_inches = 0.1)


def ariplotinterpcrestcalc(agnes, return_interval, storm_name, monthyear):
            agnes = agnes.dropna()
            minlat = agnes['Lat'].min()
            minlon = agnes['Lon'].min()
            maxlat = agnes['Lat'].max()
            maxlon = agnes['Lon'].max()
            import pyproj



            import matplotlib.pyplot as plt
            import matplotlib
        #    fig = plt.figure(figsize=(15, 15))
            import cartopy
            import cartopy.crs as ccrs
            import cartopy.feature as cf
            fig = plt.figure(figsize=(15, 15))

            proj = ccrs.PlateCarree()

            ax1 = fig.add_subplot(1,1,1,projection=proj)
            ax1.set_title(storm_name +" "+return_interval + " ARIs and Record Crests", loc='left', size = 20)
            border_resolution = '10m'  # Adjust the resolution as needed
            ax1.coastlines(resolution=border_resolution, linewidth=0.8)
            ax1.add_feature(cfeature.BORDERS, edgecolor=[.3, .3, .3], linewidth=0.5)
            ax1.add_feature(cfeature.STATES.with_scale('10m'), edgecolor=[.3, .3, .3], linewidth=0.5)
    #        ax1.add_feature(cfeature.STATES, edgecolor='gray', linewidth=0.5)

            import pandas as pd
            import numpy as np
            import matplotlib.pyplot as plt
            from scipy.interpolate import griddata


            # Define the grid for interpolation (latitude and longitude ranges)
            latitude_grid = np.linspace(agnes['Lat'].min(), agnes['Lat'].max(), 100)
            longitude_grid = np.linspace(agnes['Lon'].min(), agnes['Lon'].max(), 100)


            # Create a meshgrid for latitude and longitude
            latitude_mesh, longitude_mesh = np.meshgrid(latitude_grid, longitude_grid)

            # Perform linear interpolation using griddata
            interpolated_precip = griddata(
                (agnes['Lat'], agnes['Lon']), agnes['ARI']*1.5,
                (latitude_mesh, longitude_mesh),
                method='linear'
            )

            colors = ['orange','darkorange','red','firebrick','deeppink', 'darkviolet', 'slateblue','blue','darkblue']
            ARIs = [1,2,5,10,25,50,100,200,500,1000]

            cmap = matplotlib.colors.ListedColormap(colors)

    #                cmap = matplotlib.colors.ListedColormap(colors)
            cmap.set_over('limegreen')
            cmap.set_under('white')



            bounds = ARIs
            norm = matplotlib.colors.BoundaryNorm(bounds, cmap.N)



            # Create a contour plot
            plt.contourf(longitude_mesh, latitude_mesh, interpolated_precip, transform=ccrs.PlateCarree(),\
            cmap=cmap,norm=norm,levels=bounds, ticks=bounds, extend='both')
    #        plt.colorbar(label='Precipitation')


        #    ax1.set_extent([-74.5,-81,39.5,42.5],crs=ccrs.PlateCarree()) # select region # select region

    #        plt.text(minlon - 2.5, minlat - 4, 'Sum = ' + str(num_ones), fontsize=20, transform=ccrs.PlateCarree(), color='black')
            # Plot the grid
            #plt.pcolormesh(lon_grid, lat_grid, values)
            plt.colorbar(fraction=0.03)


            import marfc_list as ma
            import pandas as pd
            import matplotlib.pyplot as plt
            import matplotlib
            import numpy as np

            from IPython.display import HTML


            #bigtext = ma.olist() + ma.rlist() + ma.clist() + ma.alist() + ma.mblist() + ma.wlist() + ma.slist()
            bigtext = open("nationalrivers.txt", "r")
            bigtext = (bigtext.read())
            import ast
            bigtext = ast.literal_eval(bigtext)

            Title = []
            Latitude=[]
            Longitude = []
            Location = []
            Rankings = []
            One = []
            for i in bigtext:
                Title.append(i[0])
                Latitude.append(float(i[1][0]))
                Longitude.append(float(i[1][1]))
                Location.append(i[1])
                Rankings.append(i[2])

            df = {'Title':Title,
                'Location':Location,
                'Latitude':Latitude,
                'Longitude':Longitude,
                'Rankings':Rankings}
            df = pd.DataFrame(df)
            print(minlon)
            print(df['Longitude'][0])

            df = df[df['Latitude']>minlat]
            df = df[df['Latitude']<maxlat]
            df = df[df['Longitude']>(-1*maxlon)]
            df = df[df['Longitude']<(-1*minlon)]
            df=df.reset_index()

            One = []
            Two = []
            Three = []

            for i in df['Rankings']:
                oneb = i.index('(1)')+4
                i = i[oneb:]
                oneb = i.index('on') + 3
                onee = i.index('<b')
                one = i[oneb:onee]
                One.append(one)

                twob = i.index('(2)')+4
                i = i[twob:]
                twob = i.index('on') + 3
                twoe = i.index('<b')
                two = i[twob:twoe]
                Two.append(two)

                try:
                    threeb = i.index('(3)')+4
                    i = i[threeb:]
                    threeb = i.index('on') + 3
                    threee = i.index('<b')
                    three = i[threeb:threee]
                    Three.append(three)
                except:
                    Three.append('01/01/1900')
            df['OneD'] = One
            df['TwoD'] = Two
            df['ThreeD'] = Three



            MY = []
            yearl = []
            months=[]
            for i in df['OneD']:
                month = i[:2]
                year = i[6:10]
                yearl.append(int(year))
                months.append(int(year[:3]))
                MY.append(month + '/' + year)

            df['MY'] = MY
            df['month'] = months
            df['year'] = yearl

            MY2 = []
            yearl2=[]
            for i in df['TwoD']:
                month = i[:2]
                year = i[6:10]
                yearl2.append(year)
                MY2.append(month + '/' + year)

            df['MY2'] = MY2
            df['year2'] = yearl2

            MY3 = []
            yearl3=[]
            for i in df['ThreeD']:
                month = i[:2]
                year = i[6:10]
                yearl3.append(year)
                MY3.append(month + '/' + year)

            df['MY3'] = MY3
            df['year3'] = yearl3

            June1972 = df[df['MY']==monthyear]

            for i in June1972['Location']:
                plt.plot(-float(i[1]), float(i[0]), color='yellow', linewidth=3, marker='s', transform=ccrs.Geodetic())

            ax1.add_feature(cfeature.OCEAN.with_scale('10m'), zorder=100, edgecolor='lightblue', facecolor='lightblue', linewidth=0.5)  # High-resolution ocean border

    #        plt.text(-120, 31, '3rd crest (n = ' + str(len(June1972)) + ')', fontsize=20, transform=ccrs.PlateCarree(), color='red')
            plt.savefig(storm_name + 'interparicrest.png', bbox_inches = 'tight', pad_inches = 0.1)

            # Inside the main function
            contour_plot = plt.contourf(longitude_mesh, latitude_mesh, interpolated_precip, transform=ccrs.PlateCarree(),
                                        cmap=cmap, norm=norm, levels=bounds, ticks=bounds, extend='both')

            # Get the collections object from the contour plot
            collections = contour_plot.collections

            # Calculate the areas of different color bands
            for i, collection in enumerate(collections):
                paths = collection.get_paths()
                total_area = 0.0
                for path in paths:
                    vertices = path.to_polygons()[0]
                    total_area += calculate_polygon_area(vertices)
                print(f"Area of color band {i + 1}: {total_area} square degree")

def open_tar_file():
    import tarfile
    import requests

#    URL for the TAR file
    tar_url = "https://ftp.wpc.ncep.noaa.gov/shapefiles/qpf/5day/QPF120hr_Day1-5_latest.tar"

    # Download the TAR file
    tar_response = requests.get(tar_url)

    # Save the TAR file locally
    with open("QPF120hr_Day1-5_latest.tar", "wb") as tar_file:
        tar_file.write(tar_response.content)

    import geopandas as gpd
    import matplotlib.pyplot as plt
    from shapely.geometry import Point

    # Extract the contents of the TAR file
    with tarfile.open("QPF120hr_Day1-5_latest.tar", "r") as tar:
        tar.extractall(path="extracted_files")

    import os

    # List all files in the extracted directory
    extracted_files = os.listdir("extracted_files")
    print(extracted_files)

    # Read the necessary files using GeoPandas
    shp_file = "extracted_files/95e0412.shp"  # Update with your actual shapefile name
    dbf_file = "extracted_files/95e0412.dbf"  # Update with your actual DBF file name

    data = gpd.read_file(shp_file)
    dbf_data = gpd.read_file(dbf_file)

    return(data,dbf_data)

def qpf(lat,lon, data, dbf_data):
    import geopandas as gpd
    import requests
    import tarfile
    import matplotlib.pyplot as plt
    from shapely.geometry import Point
    import os

    # Define a function to get QPF forecast for given lat/lon
    def get_polygons_for_point(latitude, longitude):
        point = Point(longitude, latitude)
        polygons = data[data.geometry.contains(point)]
        return polygons

    # Example coordinates for New York City
    nyc_latitude = lat
    nyc_longitude = lon

    # Get QPF forecast for NYC
    qpf_nyc = get_polygons_for_point(nyc_latitude, nyc_longitude)
    print(len(qpf_nyc))
    if len(qpf_nyc)==0:
        return(0)


    def get_highest_qpf_value(data):
        highest_qpf_row = data.loc[data['QPF'].idxmax()]
        return highest_qpf_row
    return(get_highest_qpf_value(qpf_nyc)['QPF'])

def calculate_polygon_area(vertices):
    from shapely.geometry import Polygon
    return Polygon(vertices).area


def snowtotalplot(agnes, return_interval, storm_name, monthyear):
        agnes = agnes.dropna()
        agnes = agnes[agnes['Total'] != 0.0].reset_index(drop=True)
        minlat = agnes['Lat'].min()
        minlon = agnes['Lon'].min()
        maxlat = agnes['Lat'].max()
        maxlon = agnes['Lon'].max()


        import matplotlib.pyplot as plt
        import matplotlib
    #    fig = plt.figure(figsize=(15, 15))
        import cartopy
        import cartopy.crs as ccrs
        import cartopy.feature as cf
        fig = plt.figure(figsize=(15, 15))

        proj = ccrs.PlateCarree()
        ax1 = fig.add_subplot(1,1,1,projection=proj)
        ax1.set_title(storm_name +" "+return_interval + " Total Snow (Inches)", loc='left', size = 20)
        plt.text(minlon, minlat-0.5, "Data from ACIS. Plot by JF", fontsize=10, color= 'black', transform=ccrs.PlateCarree())
        border_resolution = '10m'  # Adjust the resolution as needed
        ax1.coastlines(resolution=border_resolution, linewidth=0.8)
#        ax1.add_feature(cfeature.BORDERS, edgecolor=[.3, .3, .3], linewidth=0.5, linestyle=':')
        ax1.add_feature(cfeature.STATES.with_scale('10m'), edgecolor=[.3, .3, .3], linewidth=1)
        ax1.add_feature(cfeature.BORDERS.with_scale('10m'), edgecolor=[.3, .3, .3], linewidth=1)

#        ax1.add_feature(cfeature.STATES, edgecolor='gray', linewidth=0.5)

        import pandas as pd
        import numpy as np
        import matplotlib.pyplot as plt
        from scipy.interpolate import griddata


        # Define the grid for interpolation (latitude and longitude ranges)
        latitude_grid = np.linspace(agnes['Lat'].min(), agnes['Lat'].max(), 100)
        longitude_grid = np.linspace(agnes['Lon'].min(), agnes['Lon'].max(), 100)


        # Create a meshgrid for latitude and longitude
        latitude_mesh, longitude_mesh = np.meshgrid(latitude_grid, longitude_grid)

        # Perform linear interpolation using griddata
        interpolated_precip = griddata(
            (agnes['Lat'], agnes['Lon']), agnes['Total'],
            (latitude_mesh, longitude_mesh),
            method='linear'
        )

        colors = ([(60/255, 60/255, 60/255), (218/255, 218/255, 218/255), (180/255, 180/255, 180/255),(128/255, 128/255, 128/255),(97/255, 222/255, 204/255), (72/255, 171/255, 167/255), (81/255, 202/255, 249/255), (45/255, 146/255, 247/255), (27/255, 70/255, 246/255), (216/255, 85/255, 199/255), (189/255, 82/255, 248/255), (183/255, 58/255, 152/255), (93/255, 35/255, 86/255), (50/255, 22/255, 51/255)])
        ARIs = [0,0.1,1,2,3,4,6,8,10,14,18,24,36,48,60]

        cmap = matplotlib.colors.ListedColormap(colors)


        bounds = ARIs
        norm = matplotlib.colors.BoundaryNorm(bounds, cmap.N)


        plt.contourf(longitude_mesh, latitude_mesh, interpolated_precip, transform=ccrs.PlateCarree(),\
        cmap=cmap,norm=norm,levels=bounds, ticks=bounds, extend='max')

        cbar = plt.colorbar(fraction=0.02)


        cbar.set_ticks(bounds)
        cbar.set_ticklabels([str(ari) for ari in bounds])


        ax1.add_feature(cfeature.OCEAN.with_scale('10m'), zorder=100, edgecolor='lightblue', facecolor='lightblue', linewidth=0.5)  # High-resolution ocean border
        ax1.add_feature(cfeature.LAKES.with_scale('10m'), zorder=100, edgecolor='lightblue', facecolor='lightblue', linewidth=0.5)  # High-resolution ocean border

        plt.savefig(storm_name + 'snowtotals.png', bbox_inches = 'tight', pad_inches = 0.1)


def snowtotalplot_alt(agnes, return_interval, storm_name, monthyear):
        agnes = agnes.dropna()
        agnes = agnes[agnes['Total'] != 0.0].reset_index(drop=True)
        minlat = agnes['Lat'].min()
        minlon = agnes['Lon'].min()
        maxlat = agnes['Lat'].max()
        maxlon = agnes['Lon'].max()


        import matplotlib.pyplot as plt
        import matplotlib
    #    fig = plt.figure(figsize=(15, 15))
        import cartopy
        import cartopy.crs as ccrs
        import cartopy.feature as cf
        fig = plt.figure(figsize=(15, 15))

        proj = ccrs.PlateCarree()
        ax1 = fig.add_subplot(1,1,1,projection=proj)
        ax1.set_title(storm_name +" "+return_interval + " Total Snow (Inches)", loc='left', size = 20)
        plt.text(minlon, minlat-0.5, "Data from ACIS. Plot by JF", fontsize=10, color= 'black', transform=ccrs.PlateCarree())

        border_resolution = '10m'  # Adjust the resolution as needed
        ax1.coastlines(resolution=border_resolution, linewidth=0.8)
#        ax1.add_feature(cfeature.BORDERS, edgecolor=[.3, .3, .3], linewidth=0.5, linestyle=':')
        ax1.add_feature(cfeature.STATES.with_scale('10m'), edgecolor=[.3, .3, .3], linewidth=1)
        ax1.add_feature(cfeature.BORDERS.with_scale('10m'), edgecolor=[.3, .3, .3], linewidth=1)

#        ax1.add_feature(cfeature.STATES, edgecolor='gray', linewidth=0.5)

        import pandas as pd
        import numpy as np
        import matplotlib.pyplot as plt
        from scipy.interpolate import griddata


        # Define the grid for interpolation (latitude and longitude ranges)
        latitude_grid = np.linspace(agnes['Lat'].min(), agnes['Lat'].max(), 100)
        longitude_grid = np.linspace(agnes['Lon'].min(), agnes['Lon'].max(), 100)


        # Create a meshgrid for latitude and longitude
        latitude_mesh, longitude_mesh = np.meshgrid(latitude_grid, longitude_grid)

        # Perform linear interpolation using griddata
        interpolated_precip = griddata(
            (agnes['Lat'], agnes['Lon']), agnes['Total'],
            (latitude_mesh, longitude_mesh),
            method='linear'
        )

        colors = (['white', (108/255, 174/255, 214/255),(85/255, 148/255, 196/255),(47/255, 110/255, 165/255),(9/255, 39/255, 150/255), (253/255, 249/255, 147/255), (249/255, 196/255, 70/255), (242/255, 135/255, 59/255), (220/255, 51/255, 47/255), (158/255, 34/255, 31/255), (104/255, 19/255, 16/255), (87/255, 42/255, 87/255), (212/255, 212/255, 252/255)])
        ARIs = [0,1,2,3,4,6,8,12,18,24,36,48,60]

        cmap = matplotlib.colors.ListedColormap(colors)


        bounds = ARIs
        norm = matplotlib.colors.BoundaryNorm(bounds, cmap.N)


        plt.contourf(longitude_mesh, latitude_mesh, interpolated_precip, transform=ccrs.PlateCarree(),\
        cmap=cmap,norm=norm,levels=bounds, ticks=bounds, extend='max')

        cbar = plt.colorbar(fraction=0.02)


        cbar.set_ticks(bounds)
        cbar.set_ticklabels([str(ari) for ari in bounds])


        ax1.add_feature(cfeature.OCEAN.with_scale('10m'), zorder=100, edgecolor='lightblue', facecolor='lightblue', linewidth=0.5)  # High-resolution ocean border
        ax1.add_feature(cfeature.LAKES.with_scale('10m'), zorder=100, edgecolor='lightblue', facecolor='lightblue', linewidth=0.5)  # High-resolution ocean border

        plt.savefig(storm_name + 'snowtotals_alt.png', bbox_inches = 'tight', pad_inches = 0.1)

def wpcize(agnes):
    data,dbf_data=rm.open_tar_file()

    print(agnes)

    qpfs=[]
    n = 0
    while n < len(agnes):
        qpf = rm.qpf(agnes['Lat'][n],agnes['Lon'][n],data,dbf_data)
        qpfs.append(qpf)
        n=n+1

    agnes['QPF']=qpfs
    agnes['Total']=agnes['Total']+agnes['QPF']

    print(agnes)
    rm.totalplotinterpcrest(agnes, return_interval, storm_name, month+'/'+year)

    agnes, return_interval, storm_name=rm.arize(agnes, return_interval, storm_name)

    rm.ariplotinterpcrest(agnes, return_interval, storm_name, month+'/'+year)
