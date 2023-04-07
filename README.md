# Python scripts for grabbing data from OFAC's Specially Designated Nationals (SDN) list

* [parse_sdn.py](parse_sdn.py)
   * Downloads the [official SDN list from OFAC](https://home.treasury.gov/policy-issues/financial-sanctions/specially-designated-nationals-list-data-formats-data-schemas)
   * Parses the xml, and creates the file [parsed_sdn.csv](data/parsed_sdn.csv), with the following four columns
     * detail - the detailed name of the entity (this is where a cryptocurrency address would be stored
     * names - a list of names given to the entity (comma separated)
     * start0 - start from date 
     * start1 - start to date
     * end0 - end from date
     * end1 - end to date
* [check_address.py](check_address.py) - a script to check whether SDN "details" are valid cryptocurrency addresses on a variety of different blockchains.  Data saved to [data/tagged_addresses.csv](data/tagged_addresses.csv)
* [get_contract_logs.py](get_contract_logs.py) - generic script to get all the events from a target Ethereum contract (requires a local Ethereum node to run)
* [get_tornado_deploy_blocks.py](get_tornado_deploy_blocks.py) - gets the block heights where the Tornado Cash contracts in the SDN list were deployed.  Data saved to [data/tornado_deploys.csv](data/tornado_deploys.csv)
* [get_tornado_logs.py](get_tornado_logs.py) - gets all the events from all the Tornado Cash contracts on the SDN list and stores them in the data/ folder
* [utils.py](utils.py) - helper script to get contract data from Etherscan
* [blockchain_stats.py](blockchain_stats.py) - Displays some basic summary statistics about how many entries on the SDN list correspond to cryptocurrency addresses
* [get_eth_transfer.py](get_eth_transfer.py) - Collects up/downstream transfers of these 71 Ethereum wallets 
* [process_eth_transfer.py](process_eth_transfer.py) - Convert blocknumber of ETH transfers to date time format
* [eth_transfer_network.py](eth_transfer_network.py) - Visualize the network of ETH transfers
	
|Chain|Number of Entries|
|------|------|
|Bitcoin|291|
|Ethereum|71|
|Tron|1|
|Ripple|1|
|Dogecoin|1|
