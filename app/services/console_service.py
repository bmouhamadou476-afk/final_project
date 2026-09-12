{
  "message": "Topologie déployée et configuration lancée",
  "gns3_version": {
    "local": true,
    "version": "2.2.59"
  },
  "project": {
    "name": "TP_IaC_Reseaux_M1",
    "project_id": "a71629b6-2d1a-435c-88c2-757c23cf763a"
  },
  "nombre_nodes": 8,
  "nombre_links": 8,
  "nodes_created": [
    {
      "name": "R1",
      "node_id": "d10a634c-e129-4bf7-8119-8f168cb8130a",
      "template": "c7200",
      "node_type": "dynamips"
    },
    {
      "name": "R2",
      "node_id": "ba26f7d3-bb44-4d67-820d-da332863cb09",
      "template": "c7200",
      "node_type": "dynamips"
    },
    {
      "name": "SW1",
      "node_id": "23ecb223-2fa6-490e-a385-b9649d96e669",
      "template": "Ethernet switch",
      "node_type": "ethernet_switch"
    },
    {
      "name": "SW2",
      "node_id": "b1a40c82-2e48-41c9-a087-d284e769a1a2",
      "template": "Ethernet switch",
      "node_type": "ethernet_switch"
    },
    {
      "name": "SWMGT",
      "node_id": "f1199112-4948-414c-8a93-9b64fb2a001c",
      "template": "Ethernet switch",
      "node_type": "ethernet_switch"
    },
    {
      "name": "NAT1",
      "node_id": "4b9ebfdb-a1cd-48a0-8da6-1512da433ed0",
      "template": "NAT",
      "node_type": "nat"
    },
    {
      "name": "PC1",
      "node_id": "c13306d3-af6b-4256-8c87-a5bd888b2cf7",
      "template": "VPCS",
      "node_type": "vpcs"
    },
    {
      "name": "PC2",
      "node_id": "6460b42e-ea3f-4140-8440-694a38694a52",
      "template": "VPCS",
      "node_type": "vpcs"
    }
  ],
  "links_created": [
    {
      "source": "PC1",
      "destination": "SW1",
      "link_id": "dbff2afe-7240-4bc3-b85e-ee36b0861fce"
    },
    {
      "source": "SW1",
      "destination": "R1",
      "link_id": "16482649-d57d-42e6-908d-738a0ce6283c"
    },
    {
      "source": "R1",
      "destination": "R2",
      "link_id": "62bda4b5-b01f-462e-86fd-8390032a2f17"
    },
    {
      "source": "R2",
      "destination": "SW2",
      "link_id": "e7bb5ded-7d28-4c92-9956-3ddb5b57d600"
    },
    {
      "source": "SW2",
      "destination": "PC2",
      "link_id": "348e2ced-8fc9-4846-ba49-b0155fd9b800"
    },
    {
      "source": "R1",
      "destination": "SWMGT",
      "link_id": "2853159c-5be4-4e61-9991-3bf352cc5a4b"
    },
    {
      "source": "R2",
      "destination": "SWMGT",
      "link_id": "95b86846-d865-4503-893b-d9465cf33e53"
    },
    {
      "source": "SWMGT",
      "destination": "NAT1",
      "link_id": "ba7de825-5687-44e6-b87e-3987ed6d6bf7"
    }
  ],
  "nodes_started": [
    {
      "name": "R1",
      "node_id": "d10a634c-e129-4bf7-8119-8f168cb8130a",
      "status": "started"
    },
    {
      "name": "R2",
      "node_id": "ba26f7d3-bb44-4d67-820d-da332863cb09",
      "status": "started"
    },
    {
      "name": "SW1",
      "node_id": "23ecb223-2fa6-490e-a385-b9649d96e669",
      "status": "started"
    },
    {
      "name": "SW2",
      "node_id": "b1a40c82-2e48-41c9-a087-d284e769a1a2",
      "status": "started"
    },
    {
      "name": "SWMGT",
      "node_id": "f1199112-4948-414c-8a93-9b64fb2a001c",
      "status": "started"
    },
    {
      "name": "NAT1",
      "node_id": "4b9ebfdb-a1cd-48a0-8da6-1512da433ed0",
      "status": "started"
    },
    {
      "name": "PC1",
      "node_id": "c13306d3-af6b-4256-8c87-a5bd888b2cf7",
      "status": "started"
    },
    {
      "name": "PC2",
      "node_id": "6460b42e-ea3f-4140-8440-694a38694a52",
      "status": "started"
    }
  ],
  "routers_configuration": [
    {
      "node": "R1",
      "status": "error",
      "error": "TCP connection to device failed.\n\nCommon causes of this problem are:\n1. Incorrect hostname or IP address.\n2. Wrong TCP port.\n3. Intermediate firewall blocking access.\n\nDevice settings: cisco_ios 192.168.100.11:22\n\n"
    },
    {
      "node": "R2",
      "status": "error",
      "error": "TCP connection to device failed.\n\nCommon causes of this problem are:\n1. Incorrect hostname or IP address.\n2. Wrong TCP port.\n3. Intermediate firewall blocking access.\n\nDevice settings: cisco_ios 192.168.100.12:22\n\n"
    }
  ]
}