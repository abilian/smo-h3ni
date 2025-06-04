"""VIM business logic."""

import requests
from werkzeug.exceptions import NotFound, BadRequest

from models import db, VIM


def sync_vims(nfvcl_base_url):
    # Fetch data from external API
    response = requests.get(f'{nfvcl_base_url}/v1/topology/')
    response.raise_for_status()
    topology_data = response.json()

    # Process and insert data into database
    added_vims = []
    for vim_data in topology_data.get('vims', []):
        # Check if a VIM with the same name already exists
        existing_vim = db.session.query(VIM).filter_by(vim_name=vim_data.get('name', '')).first()
        if existing_vim is None:
            vim = VIM(
                pop_area=vim_data.get('areas', [])[0],
                vim_name=vim_data.get('name', ''),
                vim_url=vim_data.get('vim_url', ''),
                vim_type=vim_data.get('vim_type', ''),
                vim_networks=vim_data.get('networks', []),
                use_floating_ip=vim_data.get('config', {}).get('use_floating_ip', False)
            )

            # Set default mgmt and service networks... can be changed
            if len(vim.vim_networks) > 1:
                vim.mgmt_network = vim.vim_networks[0]
                vim.service_network = vim.vim_networks[1]

            db.session.add(vim)
            db.session.commit()
            added_vims.append(vim.as_dict())  # Include ID in the response

    if added_vims:
        # If new VIMs are added, return success message with new VIMs
        return {'message': 'VIMs added successfully', 'vims': added_vims}
    else:
        # If no new VIMs are added, fetch existing VIMs from the database
        existing_vims = db.session.query(VIM).all()
        existing_vims_data = [vim.as_dict() for vim in existing_vims]
        if existing_vims_data:
            return {'message': 'No new VIMs obtained by the NFVCL. Existing VIMs:',
                    'vims': existing_vims_data}
        else:
            return {'message': 'No new VIMs obtained by the NFVCL and no existing VIMs in the database.'}


def fetch_vim(smo_id):
    # Find VIM by smo_id
    vim = db.session.query(VIM).filter_by(id=smo_id).first()
    if not vim:
        raise NotFound(f'VIM with SMO ID {smo_id} not found')
    return vim.as_dict()


def remove_vim(smo_id):
    # Find and delete the VIM
    vim = db.session.query(VIM).filter_by(id=smo_id).first()
    if not vim:
        raise NotFound(f'VIM with SMO ID {smo_id} not found')
    response = requests.delete(f'/v1/topology/vim/{vim.vim_name}')
    response.raise_for_status()  # Raise an exception for HTTP errors (e.g., 404, 500)
    nfvcl_response = response.json()

    db.session.delete(vim)
    db.session.commit()
    return {'message': f'VIM with SMO ID {smo_id} deleted successfully',
            'NFVCL_Response': nfvcl_response}


def fetch_all_vims(pop_area):
    if pop_area:
        vims = db.session.query(VIM).filter_by(pop_area=pop_area).first()
    else:
        vims = db.session.query(VIM).all()
    if vims:
        if type(vims) is list:
            list_vims = [vim.as_dict() for vim in vims]
        else:
            list_vims = vims.as_dict()
        return {'SMO VIMs': list_vims}
    else:
        return "No Registered VIMs (or check pop_area)"


def create_vim(nfvcl_base_url, data):
    # Extract data from the request
    try:
        topology_name = data['topology']
        pop_area = data['pop_area']
        vim_name = data['vim_name']
        vim_tenant_name = data['vim_tenant_name']
        vim_user = data['vim_user']
        vim_password = data['vim_password']
        vim_url = data['vim_url']
        mgmt_network = data['mgmt_network']
        service_network = data['service_network']
        use_floating_ip = data['use_floating_ip']
    except KeyError as e:
        raise BadRequest(str(e))

    nfvcl_request_body = {
        "id": topology_name,
        "callback": None,
        "vims": [{
            "name": vim_name,
            "vim_type": "openstack",
            "schema_version": "1.0",
            "vim_url": vim_url,
            "vim_tenant_name": vim_tenant_name,
            "vim_user": vim_user,
            "vim_password": vim_password,
            "config": {
                "insecure": True,
                "APIversion": "v3.3",
                "use_floating_ip": use_floating_ip
            },
            "networks": [mgmt_network.get("name"), service_network.get("name")],
            "areas": [pop_area]
        }],
        "kubernetes": [],
        "networks": [{
            "name": mgmt_network.get("name"),
            "external": False,
            "type": "vxlan",
            "vid": None,
            "dhcp": True,
            "cidr": mgmt_network.get("cidr"),
            "gateway_ip": mgmt_network.get("gateway"),
            }, {
            "name": service_network.get("name"),
            "external": False,
            "type": "vxlan",
            "vid": None,
            "dhcp": True,
            "ids": [],
            "cidr": service_network.get("cidr"),
            "gateway_ip": service_network.get("gateway"),
        }],
        "routers": [],
        "pdus": [],
        "prometheus_srv": []
    }

    response = requests.post(f'{nfvcl_base_url}/v1/topology', json=nfvcl_request_body)
    response.raise_for_status()  # Raise an exception for HTTP errors (e.g., 404, 500)
    nfvcl_response = response.json()

    # Create a new VIM instance
    new_vim = VIM(
        pop_area=pop_area,
        vim_name=vim_name,
        vim_url=vim_url,
        vim_type='Openstack',  # Assuming vim_type is always 'Openstack'
        vim_networks=[mgmt_network.get("name"), service_network.get("name")],
        mgmt_network=mgmt_network.get("name"),
        service_network=service_network.get("name"),
        use_floating_ip=use_floating_ip
    )

    # Add the new VIM instance to the database
    db.session.add(new_vim)
    db.session.commit()

    return {'message': 'OS K8S cluster created successfully',
            'NFVCL_Response': nfvcl_response,
            'vim': new_vim.as_dict()}


# def remove_vim_name_area(vim_name, pop_area):
#     # Find and delete the VIM
#     vim = db.session.query(VIM).filter_by(vim_name=vim_name, pop_area=pop_area).first()
#     if not vim:
#         raise NotFound(f'VIM {vim_name} in POP area {pop_area} not found.')
#     db.session.delete(vim)
#     db.session.commit()
#     return {'message': f'VIM {vim_name} in POP area {pop_area} deleted successfully'}
