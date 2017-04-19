import json
import unittest
import uuid

from cloudbridge.cloud.interfaces import TestMockHelperMixin

from test.helpers import ProviderTestBase
import test.helpers as helpers


class AzureSecurityServiceTestCase(ProviderTestBase):
    def __init__(self, methodName, provider):
        super(AzureSecurityServiceTestCase, self).__init__(
            methodName=methodName, provider=provider)
        self.key_pairs = self.provider.security.key_pairs
        self.security_groups = self.provider.security.security_groups

    @helpers.skipIfNoService(['security.security_groups'])
    def test_azure_security_group_create(self):
        name = "testCreateSecGroup3"
        sg = self.security_groups.create(
            name=name, description=name, network_id="")
        print("Create( " + "Name-" + sg.name + "  Id-" + sg.id + " Rules - " + str(sg.rules) + " )")
        self.assertEqual(name, sg.name)

    @helpers.skipIfNoService(['security.security_groups'])
    def test_azure_security_group_find(self):
        with self.assertRaises(NotImplementedError):
            sgs = self.security_groups.find("mygroup")

    @helpers.skipIfNoService(['security.security_groups'])
    def test_azure_security_group_list(self):
        sgl = self.security_groups.list()
        found_sg = [g.name for g in sgl]
        for group in sgl:
            print("List( " + "Name-" + group.name + "  Id-" + group.id + " Rules - " + " )")
        self.assertTrue(
            len(sgl) == 3,
            "Count should be 3")

    @helpers.skipIfNoService(['security.security_groups'])
    def test_azure_security_group_get_found(self):
        sgl = self.security_groups.get("/subscriptions/7904d702-e01c-4826-8519-f5a25c866a96/resourceGroups/CloudBridge-Azure/providers/Microsoft.Network/networkSecurityGroups/sg3")
        print("Get ( " + "Name - " + sgl.name + "  Id - " + sgl.id + " )")
        self.assertTrue(
            sgl.name == "sg3",
            "SG name should be sg3")

    @helpers.skipIfNoService(['security.security_groups'])
    def test_azure_security_group_get_not_found(self):
        sgl = self.security_groups.get("/subscriptions/7904d702-e01c-4826-8519-f5a25c866a96/resourceGroups/CloudBridge-Azure/providers/Microsoft.Network/networkSecurityGroups/sg4")
        print(str(sgl))
        self.assertTrue(
            sgl == None,
            "Security group does not exist. Should return None.")

    @helpers.skipIfNoService(['security.security_groups'])
    def test_azure_security_group_delete_IdExists(self):
        sg = self.security_groups.delete("/subscriptions/7904d702-e01c-4826-8519-f5a25c866a96/resourceGroups/CloudBridge-Azure/providers/Microsoft.Network/networkSecurityGroups/sg2")
        print("Delete - ")
        self.assertEqual(sg, True)

    @helpers.skipIfNoService(['security.security_groups'])
    def test_azure_security_group_delete_IdNotExist(self):
        sg = self.security_groups.delete("/subscriptions/7904d702-e01c-4826-8519-f5a25c866a96/resourceGroups/CloudBridge-Azure/providers/Microsoft.Network/networkSecurityGroups/sg5")
        self.assertEqual(sg, False)

    @helpers.skipIfNoService(['security.security_groups'])
    def test_azure_security_group_rule_create(self):
        list = self.security_groups.list()
        cb = list.data[0]
        rules = cb.rules
        for rule in rules:
            print(str(rule))
        print("Before creating Rule -  " + str(rules[0]) + " length - " + str(len(rules)))
        cb.add_rule('*', '25', '100', '*')
        rules = cb.rules
        print("After creating Rule -  " + str(rules[0]) + " length - " + str(len(rules)))
        self.assertEqual(len(rules), 3)

    @helpers.skipIfNoService(['security.security_groups'])
    def test_azure_security_group_rule_delete(self):
        list = self.security_groups.list()
        cb = list.data[0]
        rules = cb.rules
        print("Before deleting Rule -  " + str(rules[0]) + " length - " + str(len(rules)))
        rules[1].delete()
        rules = cb.rules
        print("After deleting Rule -  " + str(rules[0]) + " length - " + str(len(rules)))
        self.assertEqual(len(rules), 2)

    @helpers.skipIfNoService(['security.security_groups'])
    def test_azure_security_group_rule_delete_Default(self):
        list = self.security_groups.list()
        cb = list.data[0]
        rules = cb.rules
        print("Before deleting Rule -  " + str(rules[0]) + " length - " + str(len(rules)))

        with self.assertRaises(Exception):
            rules[0].delete()

    @helpers.skipIfNoService(['security.security_groups'])
    def test_azure_security_group_rule_get_exist(self):
        list = self.security_groups.list()
        cb = list.data[0]
        rule = cb.get_rule('*', '25', '1', '100')
        print("Get Rule -  " + str(rule))
        self.assertEqual(str(rule), "<CBSecurityGroupRule: IP: *; from: 25; to: 1; grp: None>")

    @helpers.skipIfNoService(['security.security_groups'])
    def test_azure_security_group_rule_get_notExist(self):
        list = self.security_groups.list()
        cb = list.data[0]
        rule = cb.get_rule('*', '25', '1', '1')
        print("Get Rule -  " + str(rule))
        self.assertEqual(str(rule), 'None')

    @helpers.skipIfNoService(['security.security_groups'])
    def test_azure_security_group_to_json(self):
        list = self.security_groups.list()
        cb = list.data[0]
        rule = cb.to_json()
        print("Get Rule -  " + str(rule))
        self.assertEqual(rule[2:4], "id")

    @helpers.skipIfNoService(['security.security_groups'])
    def test_azure_security_group_rule_to_json(self):
        list = self.security_groups.list()
        cb = list.data[0]
        rules = cb.rules
        rule = rules[0]
        json = rule.to_json()
        print("Get Rule -  " + str(json))
        self.assertEqual(json[2:9], "cidr_ip")
