# Dependencies
# ============
# Standard
# --------
from typing import List, Mapping

# Non-standard
# ------------
# See https://flask.palletsprojects.com/en/2.0.x/
from flask import Blueprint, abort, render_template, url_for

# Local
# -----
from .records import Record, Relation, Scheme, VocabTerm
from .vocab import get_thesaurus

bp = Blueprint('list', __name__)


def get_scheme_tree(records: List[Scheme], seen_so_far: List = None)\
        -> Mapping[str, str]:
    '''Takes list of parent schemes and returns tree suitable for use with the
    contents template.'''
    records.sort(key=lambda k: k.name.lower())
    if seen_so_far is None:
        seen_so_far = list()
    tree = list()
    rel = Relation()
    for record in records:
        if record.mscid in seen_so_far:
            print("WARNING: parent/child recursion error detected for"
                  f" {record.mscid}.")
            return tree
        children = rel.subject_records("parent schemes", record.mscid)
        node = {
            'name': record.name,
            'url': url_for(
                'main.display', table=record.table, number=record.doc_id),
            'children': get_scheme_tree(
                children, seen_so_far=seen_so_far + [record.mscid])
            }
        tree.append(node)
    return tree


# List of standards
# =================
@bp.route('/<string:series>-index/<any("parent schemes", "supported schemes",'
          ' "input schemes", "output schemes", "endorsed schemes",'
          ' maintainers, funders, users, originators):role>')
@bp.route('/<string:series>-index')
def record_index(series, role=None):
    '''The contents template takes a 'tree' variable, which is a list of
    dictionaries, each with keys 'name' (human-readable name) and 'url'
    (Catalog page URL). The dictionary represents a node and if the node has
    children, the dictionary has a 'children' key, the value of which is
    another tree.
    '''
    heading = f"{series}s"
    if series == "scheme" and role is None:
        # Listing metadata schemes.
        rel = Relation()

        heading = "metadata standards"
        records = Scheme.all()

        # Get blacklist of child schemes
        children = rel.subjects(predicate="parent schemes")

        # Assemble tree of records that are not on blacklist:
        tree = get_scheme_tree([
            record for record in records
            if record and record.mscid not in children])
        return render_template(
            'contents.html', title=f"Index of {heading}", tree=tree)

    # Abort if series is a vocabulary item:
    elif series == "datatype" or series in [
            c.series for c in VocabTerm.__subclasses__()]:
        abort(404)

    # Listing another type of record.
    for record_cls in Record.__subclasses__():
        if series == record_cls.series:
            # Get all of them in alphabetical order:
            if role:
                if role.endswith("schemes"):
                    if series != "scheme":
                        abort(404)
                elif series != "organization":
                    abort(404)
                heading = role
                if role == 'originators':
                    heading = 'endorsing organizations'
                rel = Relation()
                records = rel.object_records(predicate=role)
            else:
                records = [k for k in record_cls.all() if k]
            records.sort(key=lambda k: k.name)
            tree = [{
                'name': record.name,
                'url': url_for(
                    'main.display', table=record.table, number=record.doc_id)
                } for record in records if record]
            return render_template(
                'contents.html', title=f"Index of {heading}", tree=tree)
    else:
        abort(404)


# Subject index
# =============
@bp.route('/subject-index')
def subject_index():
    th = get_thesaurus()
    keywords_used = Scheme.get_used_keywords()
    tree = th.get_tree(keywords_used)
    tree.insert(0, {
        'name': 'HMC_Matter',
        'url': url_for('search.subject', subject='HMC_Matter')}) 
    tree.insert(0, {
        'name': 'HMC_Information',
        'url': url_for('search.subject', subject='HMC_Information')})
    tree.insert(0, {
        'name': 'HMC_Health',
        'url': url_for('search.subject', subject='HMC_Health')})
    tree.insert(0, {
        'name': 'HMC_Energy',
        'url': url_for('search.subject', subject='HMC_Energy')})
    tree.insert(0, {
        'name': 'HMC_EarthAndEnvironment',
        'url': url_for('search.subject', subject='HMC_EarthAndEnvironment')})
    tree.insert(0, {
        'name': 'HMC_AST',
        'url': url_for('search.subject', subject='HMC_AST')})

    return render_template(
        'contents.html', title='Index of subjects', tree=tree)
