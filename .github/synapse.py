#!/usr/bin/env python3

import asyncio
import os
import sys

from azure.identity.aio import DefaultAzureCredential
from azure.mgmt.synapse.aio import SynapseManagementClient

credential = DefaultAzureCredential()
subscription_id = os.getenv("DBT_AZURE_SUBSCRIPTION_ID")
resource_group_name = os.getenv("DBT_AZURE_RESOURCE_GROUP_NAME")
synapse_name = os.getenv("DBT_SYNAPSE_SERVER")
database_name = os.getenv("DBT_SYNAPSE_DB")


async def pause() -> bool:
    try:
        client = SynapseManagementClient(credential=credential, subscription_id=subscription_id)
        sql_pool = await client.sql_pools.get(
            resource_group_name=resource_group_name,
            workspace_name=synapse_name,
            sql_pool_name=database_name,
        )
        if sql_pool.status == "Online":
            res = await client.sql_pools.begin_pause(
                resource_group_name=resource_group_name,
                workspace_name=synapse_name,
                sql_pool_name=database_name,
            )
            print("Pausing SQL Pool")
            await res.wait()
        elif sql_pool.status in ("Pausing", "Resuming"):
            print(f"SQL Pool is {sql_pool.status}, waiting a minute and trying again")
            await asyncio.sleep(60)
            return True
        else:
            print(f"SQL Pool is already {sql_pool.status}")

        return False
    finally:
        await client.close()


async def resume() -> bool:
    try:
        client = SynapseManagementClient(credential=credential, subscription_id=subscription_id)
        sql_pool = await client.sql_pools.get(
            resource_group_name=resource_group_name,
            workspace_name=synapse_name,
            sql_pool_name=database_name,
        )
        if sql_pool.status == "Paused":
            res = await client.sql_pools.begin_resume(
                resource_group_name=resource_group_name,
                workspace_name=synapse_name,
                sql_pool_name=database_name,
            )
            print("Resuming SQL Pool")
            await res.wait()
        elif sql_pool.status in ("Pausing", "Resuming"):
            print(f"SQL Pool is {sql_pool.status}, waiting a minute and trying again")
            await asyncio.sleep(60)
            return True
        else:
            print(f"SQL Pool is already {sql_pool.status}")

        return False
    finally:
        await client.close()


async def main():
    if len(sys.argv) == 1:
        print("Usage: synapse.py [pause|resume]")
        return

    if sys.argv[1] == "pause":
        if await pause():
            await main()
    elif sys.argv[1] == "resume":
        if await resume():
            await main()
    else:
        print("Usage: synapse.py pause|resume")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
