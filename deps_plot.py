import json
import subprocess



def svg_content(package):
    print('Rendering {}'.format(package))
    with open('dependencies.json', 'r') as fh:
        dependants = json.load(fh)

    dependencies = {}
    for p, deps in dependants.items():
        for d in deps:
            dependencies.setdefault(d, []).append(p)

    graph = []

    graph.append('digraph {')
    graph.append('rankdir="LR";')
    graph.append('ranksep="2"')
    graph.append('splines=polyline;')
    graph.append('ordering=out;')
    graph.append('"{}" [shape=box fillcolor=yellow style=filled];'.format(package))

    for pkg in sorted(set(dependencies.get(package, [])) | set(dependants.get(package, []))):
        context = dict(pkg=pkg,
                       recipe_url='https://github.com/conda-forge/{0}-feedstock'.format(pkg),
                       feedstock_url='https://github.com/conda-forge/{0}-feedstock'.format(pkg),
                       deps_url='./{}'.format(pkg))
        graph.append('''
            "{pkg}" [label=<
                 <TABLE ALIGN="CENTER" CELLBORDER="0" CELLPADDING="0" CELLSPACING="0" BORDER="0" TOOLTIP="">
                          <TR><TD></TD><TD ALIGN="CENTER" HREF="{feedstock_url}">{pkg}</TD><TD></TD></TR>
                          <TR><TD HREF="{recipe_url}">recipe </TD><TD></TD><TD HREF=" {deps_url}">deps</TD></TR>
                 </TABLE>>];'''.format(**context))
        #graph.append('"{pkg}" [URL="{feedstock_url}"];'.format(**context))

    graph.append('subgraph {')
    for dep in set(dependencies.get(package, [])):
        graph.append('"{}" ->"{}";'.format(dep, package))
    graph.append('}')

    graph.append('subgraph {')
    for dep in set(dependants.get(package, [])):
        graph.append('"{}" -> "{}";'.format(package, dep))
    graph.append('}')

    graph.append('}')

    import tempfile
    with tempfile.NamedTemporaryFile(mode='w') as fh:
        fh.write('\n'.join(graph))
        fh.flush()

        with tempfile.NamedTemporaryFile(mode='w') as svg_content:
            fname = svg_content.name
            subprocess.check_call(['dot', fh.name, '-Tsvg', '-o{}'.format(fname)])
            with open(fname, 'r') as svg_content:
                return svg_content.readlines()
