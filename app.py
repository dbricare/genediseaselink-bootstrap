from flask import Flask, render_template, request, redirect
import numpy as np
import pandas as pd
import operator, os, datetime
from bokeh.plotting import figure, output_file, save, show, ColumnDataSource
from bokeh.models import HoverTool
from bokeh.resources import CDN
from bokeh.embed import components, autoload_static


app = Flask(__name__)


catclr = {'Kidneys and urinary system': '#7f7f7f', 'Food, nutrition, and metabolism': '#e377c2', 'Digestive system': '#d62728', 'Not Available': '#eeeeee', 'Brain and nervous system': '#2ca02c', 'Mouth and teeth': '#17becf', 'Reproductive system': '#ffbb78', 'Lungs and breathing': '#bcbd22', 'Bones, muscles, and connective tissues': '#ff7f0e', 'Blood/lymphatic system': '#1f77b4', 'Eyes and vision': '#8c564b', 'Ear, nose, and throat': '#9467bd', 'Skin, hair, and nails': '#98df8a'}

disease_dict = {'immune': 'Immune system', 'mouth': 'Mouth and teeth', 
                'kidney': 'Kidneys and urinary system', 
                'reproductive': 'Reproductive system', 
                'metabolism': 'Food, nutrition, and metabolism', 
                'digest': 'Digestive system', 'blood': 'Blood/lymphatic system', 
                'bone': 'Bones, muscles, and connective tissues', 
                'ent': 'Ear, nose, and throat', 'not': "Not Available",
                'endocrine': 'Endocrine system (hormones)', 'all': 'All', 
                'eye': 'Eyes and vision', 'cancer': 'Cancers', 'skin': 
                'Skin, hair, and nails', 'heart': 'Heart and circulation', 
                'mental': 'Mental health and behavior', 
                'brain': 'Brain and nervous system', 'lung': 'Lungs and breathing'}
                
atype_dict = {'all': 'All', 'genetic': 'GeneticVariation', 
              'altered': 'AlteredExpression'}
              
perc_dict = {'00': 'Not Selected', '01': 'Top 1%', '05': 'Top 5%', 
             '10': 'Top 10%', '15': 'Top 15%', '20': 'Top 20%', '25': 'Top 25%'}

@app.route('/')
def main():
    return redirect('/index')


@app.route('/index', methods=['GET', 'POST'])
def index():  #remember the function name does not need to match the URL


    # Load plot data
#     dfall = pd.read_csv('GeneDiseaseMoreCats.csv')
#     dfall = pd.read_csv('ThreeGDA.tsv',sep='\t')
    dfall = pd.read_csv('GDAallthreehigh.tsv', sep='\t')
    dfall.fillna(value='Not Available', inplace=True)
    dfstash = dfall.copy()
    
    # create pull-down menu list
    catdict = {k: v for k, v in disease_dict.items() 
               if (v in dfall.category.unique()) or (k in 'all') or (k in 'not')}
    catlist = sorted(catdict.items(), key=operator.itemgetter(1))
    atypedict = {k: v for k, v in atype_dict.items() 
               if (v in dfall.associationType.unique()) or (k in 'all') or (k in 'not')}
    atypelist = sorted(atypedict.items(), key=operator.itemgetter(1))
    perclist = sorted(perc_dict.items(), key=operator.itemgetter(0))
        
    # return user-selected data
    jump = ''
    selcat = ''
    selatype = ''
    errmsg = ''
    selperc = '00'
    if request.method=='POST':
        jump = '<script> window.location.hash="gdaplot"; </script>'
        selcat = request.form['selectioncat']
        selatype = request.form['selectiontype']
        selperc = request.form['selectioncir']
        cirrad = np.percentile(dfall['ideal'],int(selperc))
        if selcat != 'all':
            dfall = dfall[dfall['category']==disease_dict[selcat]]
        if selatype != 'all':
            dfall = dfall[dfall['associationType']==atype_dict[selatype]]
#         if selperc != '00':
        if len(dfall)==0:
            dfall = dfstash.copy()
            selcat='all'
            selatype='all'
            errmsg='No matching gene-disease associations found.'
      
    
    yy = dfall['count_total']
    xx = dfall['score_total']


    # Generate plot
    output_file("templates/index.html")

    dfall['color'] = dfall['category'].map(lambda x: catclr[x])

    source = ColumnDataSource(
        data=dict(
            x=xx,
            y=yy,
            genes=dfall['geneCount'],
            desc=dfall['diseaseName'],
            desc2=dfall['geneSymbol'],
            cat=dfall['category'],
            assoc=dfall['associationType']
        )
    )

    hover = HoverTool(tooltips=[("Disease", "@desc"), ("Category", "@cat"), 
    ("Gene", "@desc2"), ("Type", "@assoc"), ("Association", "@x{0.000}"), ("Specificity", 
    "@y{0.000}")], names=['pts'])



    p = figure(plot_width=900, plot_height=600, tools=['box_zoom','pan','reset',
    'save',hover], x_range=[0,0.8], y_range=[0,0.8], title='Gene-disease association surpassing high-scoring threshold')
    p.title_text_font = 'Source Sans Pro'
    p.xaxis.axis_label = 'Association Score'
    p.yaxis.axis_label = 'Specificity Score'
    p.xaxis.axis_label_text_font = 'Source Sans Pro'
    p.yaxis.axis_label_text_font = 'Source Sans Pro'

    if selperc != '00':
        xcir = np.linspace(-0.6,1,100)
        ycir = 1-np.sqrt(np.square(cirrad)-np.square(xcir-1))
        xcir = np.append(xcir, 1.0)
        ycir = np.append(ycir, 1.0)
        p.patch(xcir, ycir, line_color='#33ff33', fill_alpha=0.15, color='#ccffcc', 
        line_width=1)

    p.circle('x', 'y', size=20, fill_alpha=0.8, color=dfall['color'], source=source, 
    line_width=1, line_color='#000000', name='pts')
    
    p.responsive = True

#     script, div = autoload_static(p, CDN, "")
    script, div = components(p)

    t = os.path.getmtime('app.py')
    updated='{modt:%B} {modt.day}, {modt:%Y}'.format(modt=datetime.date.fromtimestamp(t))

#     updated = 'February 2, 2016'


    return render_template('index.html', script=script, div=div, catlist=catlist, atypelist=atypelist, selcat=selcat, selatype=selatype, perclist=perclist, selperc=selperc, updated=updated, jumpscript=jump, errmsg = errmsg)        


if __name__ == "__main__":
    app.run(port=33507)

