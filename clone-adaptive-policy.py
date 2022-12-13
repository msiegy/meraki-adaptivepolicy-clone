#Get Org
#Read Policy Objects, custom ACLs, Policy
#clone Objects, Acls, Policy

import meraki
import os
from dotenv import load_dotenv
import ipdb
load_dotenv()
MERAKI_DASHBOARD_API_KEY = os.environ.get('MERAKI_DASHBOARD_API_KEY')
FROM_ORGID = os.environ.get('FROM_ORGID')
TO_ORGID = os.environ.get('TO_ORGID')
dashboard = meraki.DashboardAPI()

def copyAdaptiveGroups(FROM_ORGID=FROM_ORGID, TO_ORGID=TO_ORGID):
    APGroups = dashboard.organizations.getOrganizationAdaptivePolicyGroups(organizationId = FROM_ORGID)
    for group in APGroups:
        name=group['name']
        sgt=group['sgt']
        description=group['description']
        policyobjects=group['policyObjects']
        try:
            print("Attempting to create group: ", name, sgt, description)
            dashboard.organizations.createOrganizationAdaptivePolicyGroup(TO_ORGID, name=name, sgt=sgt, description=description, policyobjects=policyobjects)
        except:
            pass

#APPolicies = dashboard.organizations.getOrganizationAdaptivePolicyPolicies(organizationId = FROM_ORGID)
#APAcls = dashboard.organizations.getOrganizationAdaptivePolicyAcls(organizationId=FROM_ORGID)

def copyAdaptiveACLs(FROM_ORGID=FROM_ORGID, TO_ORGID=TO_ORGID):
    APAcls = dashboard.organizations.getOrganizationAdaptivePolicyAcls(organizationId = FROM_ORGID)
    for acl in APAcls:
        name=acl['name']
        #print("\n", name, "\n")
        rules=acl['rules']
        description=acl['description']
        ipVersion=acl['ipVersion']
        try:
            print("Attempting to create ACL: ", name, description, rules)
            dashboard.organizations.createOrganizationAdaptivePolicyAcl(TO_ORGID, name=name, rules=rules, description=description, ipVersion=ipVersion)
        except:
            pass

def copyAdaptivePolicies(FROM_ORGID=FROM_ORGID, TO_ORGID=TO_ORGID):
    APPolicies = dashboard.organizations.getOrganizationAdaptivePolicyPolicies(organizationId = FROM_ORGID)
    newGroups = dashboard.organizations.getOrganizationAdaptivePolicyGroups(TO_ORGID)
    newACLs = dashboard.organizations.getOrganizationAdaptivePolicyAcls(TO_ORGID)

    for policies in APPolicies:
        #source and dest group values will not work, we need to find the groupIDs first since they will be different from org to org.
        #so inside loop, get name of current src and dst groups then loop through previously stored TO_ORGID group listing to extact relevant IDs.
        sourceGroup=policies['sourceGroup']
        destinationGroup=policies['destinationGroup']
        acls=policies['acls']
        lastEntryRule=policies['lastEntryRule']
        for group in newGroups:
            if group['name'] == sourceGroup['name']:
                sourceGroup['id'] = group['groupId']
            if group['name'] == destinationGroup['name']:
                destinationGroup['id'] = group['groupId']

        if acls:  #first check if there is an acl for this policy... some ACLs wiil have multiple entries...
            for acl in acls:
                print('\n\n', acls)
            
                for newacl in newACLs:
                    #ipdb.set_trace()
                    if acl['name'] == newacl['name']:
                        acl['id'] = newacl['aclId']
        try:
            print("\n\nAttempting to create policy: ", sourceGroup, destinationGroup, acls, lastEntryRule)
            dashboard.organizations.createOrganizationAdaptivePolicyPolicy(TO_ORGID, sourceGroup=sourceGroup, destinationGroup=destinationGroup, acls=acls, lastEntryRule=lastEntryRule)
        except:
            #ipdb.set_trace()
            pass

copyAdaptiveGroups(FROM_ORGID, TO_ORGID)
copyAdaptiveACLs(FROM_ORGID, TO_ORGID)
copyAdaptivePolicies(FROM_ORGID, TO_ORGID)
