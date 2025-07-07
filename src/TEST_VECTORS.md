# TEST VECTORS for infra_utils functions 

Here are reported infra_utils library function's example of correct input and expected outputs 
(used inside LoCo app)

## fetch_slots_versions_with_dinamic_filter
### Input
{
    project="CERRI"
}
### Ouput
None

## query_stb_info
### Input
{
    ip="10.170.0.199"
    slot=4
}
### Ouput
[tuple] ('eu-q-amidala-it', '0000', '10.170.0.210', '6763A3', 'it', 'STHD 07')


## get_stb_status_broken
### Input
{
    ip="10.170.0.199"
    slot=4
}
### Ouput
[bool] False

## get_broken_from_rack
### Input
{
    ip_rack="10.41.16.113"
}
### Ouput
[dict] {'rack_ip': '10.41.16.113', 'slots': [13]}

## query_stb_project_info
### Input
{
    ip="10.170.0.199"
    slot=4
}
### Output
[tuple] ('eu-q-amidala-it', '0000', '10.170.0.210', '6763A3', 'it', 'STHD 07', 'PCC')


## query_stb_project_info
### Input
{
    ip="10.170.0.199"
    slot=4
}
### Output
[tuple] ('eu-q-amidala-it', '0000', '10.170.0.210', '6763A3', 'it', 'STHD 07', 'PCC')

## get_all_stb
### Input
NO INPUT
### Output
[list] [<infra_utils.models.infradb_Iaas.InfraDBStbIaas object at 0x72892c7256a0>, ...]

## get_rack_slot_by_ip
### Input
{
    ip="10.170.0.177"
}
### Output
[tuple] "10.170.0.167", 3

## available_slots
### Input
{
    proj="CERRI"
    typ="Llama"
}
### Output
[int] 2

## get_auto_reboot
### Input
NO INPUT
### Output
[list] [{'slot': 3, 'magiq': '10.170.0.39'}, {'slot': 4, 'magiq': '10.170.0.39'}, ...]

## get_ip
### Input
{
    slot=3
    server_name="STHD 06"
    server_ip="10.170.1.71"
}
### Output
[str] '10.170.0.177'


## get_ip
### Input
{
    slot=3
    server_name="STHD 06"
    server_ip="10.170.1.71"
}
### Output
[str] '10.170.0.177'

## get_stbs_by_project
### Input
{
    proj="CERRI"
}
### Output
[list] [{'rack_ip': '10.170.1.71', 'slot': 3}, {'rack_ip': '10.170.1.71', 'slot': 8} ...]

## fetch_slots_versions
### Input
{
    proj="CERRI"
}
### Output
[list] [{'rack_ip': '10.170.1.71', 'slot': 3, 'version': 'Q310.000.08.00D'}, {'rack_ip': '10.170.1.71', 'slot': 8, 'version': 'Q270.000.09.00D'}, ...]


## fetch_rack_slot_type_by_project
### Input
{
    project="CERRI",
}
### Output
[list] [{'rack_name': '4.0 META3', 'slot': 3, 'device_type': 'Falcon'}, ...]

## fetch_rack_slot_by_project_and_type
### Input
{
    project="CERRI",
    device_type="Llama"
}
### Output
[list] [{'rack_name': '4.0 META3', 'slot': 12}, {'rack_name': '4.0 META3', 'slot': 16}]

## fetch_rack_slot_type_by_project_grouped_by_rack
### Input
{
    project="CERRI"
}
### Output
[dict] {'records': [{'rack_name': '4.0 META3', 'devices': [{'slot': 3, 'device_type': 'Falcon', ...}]}]}

## fetch_rack_slot_by_project_and_type_grouped_by_rack
### Input
{
    project="CERRI",
    device_type="Llama"
}
### Output
[dict] {'records': [{'rack_name': '4.0 META3', 'devices': [{'slot': 12}, {'slot': 16}]}]}


