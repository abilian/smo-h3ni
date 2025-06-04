"""VIM endpoints."""

from flasgger import swag_from
from flask import Blueprint, request, current_app

from services.nfvcl.vim_service import sync_vims, fetch_vim, remove_vim,\
    fetch_all_vims, create_vim

vim = Blueprint('vim', __name__, url_prefix='/vims')


@vim.route('/sync/nfvcl_vims', methods=['GET'])
@swag_from('swagger/vim/get_nfvcl_vims.yaml')
def get_nfvcl_vims():
    """Syncs all VIMs from the NFVCL instance."""

    nfvcl_base_url = current_app.config['NFVCL_BASE_URL']
    return sync_vims(nfvcl_base_url), 200


@vim.route('/smo_vims/<string:smo_id>', methods=['GET'])
@swag_from('swagger/vim/get_smo_vim.yaml')
def get_smo_vim(smo_id):
    return fetch_vim(smo_id), 200


@vim.route('/smo_vims/<string:smo_id>', methods=['DELETE'])
@swag_from('swagger/vim/delete_smo_vim.yaml')
def delete_smo_vim(smo_id):
    return remove_vim(smo_id), 200


@vim.route('/smo_vims', methods=['GET'])
@swag_from('swagger/vim/get_smo_vims.yaml')
def get_smo_vims():
    pop_area = request.args.get('pop_area')
    return fetch_all_vims(pop_area), 200


@vim.route('/smo_vims', methods=['POST'])
@swag_from('swagger/vim/post_smo_vim.yaml')
def post_smo_vim():
    nfvcl_base_url = current_app.config['NFVCL_BASE_URL']
    data = request.get_json()
    return create_vim(nfvcl_base_url, data), 201


# @vim.route('/smo_vims', methods=['DELETE'])
# @swag_from('swagger/vim/delete_vim.yaml')
# def delete_smo_vim(self):
#     vim_name = request.args.get('vim_name')
#     pop_area = request.args.get('pop_area')
#     return remove_vim_name_area(vim_name, pop_area), 200
