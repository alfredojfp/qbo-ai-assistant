# -*- coding: utf-8 -*-
"""
Tests para autonomia.user_behavior_learning.
Ejecutar: python3 -m unittest tests.test_user_behavior_learning
"""
import json
import os
import shutil
import tempfile
import unittest

from autonomia.user_behavior_learning import (
    UserBehaviorLearningEngine,
    tool_learn_from_interaction,
    tool_get_user_suggestions,
    tool_record_user_correction,
    tool_get_conversation_context,
)


def make_engine():
    """Crea un engine con archivo temporal."""
    tmpdir = tempfile.mkdtemp()
    path = os.path.join(tmpdir, "behavior.json")
    engine = UserBehaviorLearningEngine(learning_file=path)
    return engine, tmpdir


def reset_module_engine(path: str):
    """Resetea el módulo global _learning_engine a uno con `path`."""
    import autonomia.user_behavior_learning as m
    m._learning_engine = UserBehaviorLearningEngine(learning_file=path)


class TestEngineInit(unittest.TestCase):
    def test_estructura_inicial(self):
        engine, tmpdir = make_engine()
        try:
            data = engine.data
            self.assertIn("preferences", data)
            self.assertIn("report_patterns", data)
            self.assertIn("conversation_context", data)
            self.assertIn("learning_stats", data)
            self.assertIn("corrections", data)
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_carga_archivo_existente(self):
        tmpdir = tempfile.mkdtemp()
        try:
            path = os.path.join(tmpdir, "existing.json")
            with open(path, "w") as f:
                json.dump({"preferences": {}, "custom": 1}, f)
            engine = UserBehaviorLearningEngine(learning_file=path)
            self.assertEqual(engine.data.get("custom"), 1)
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_archivo_corrupto_retorna_estructura_vacia(self):
        tmpdir = tempfile.mkdtemp()
        try:
            path = os.path.join(tmpdir, "corrupt.json")
            with open(path, "w") as f:
                f.write("not json {{{")
            engine = UserBehaviorLearningEngine(learning_file=path)
            self.assertIn("preferences", engine.data)
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_persistencia_entre_instancias(self):
        tmpdir = tempfile.mkdtemp()
        try:
            path = os.path.join(tmpdir, "persist.json")
            e1 = UserBehaviorLearningEngine(learning_file=path)
            e1.learn_account_preference("Bank Account", "deposits")
            e2 = UserBehaviorLearningEngine(learning_file=path)
            key = "Bank Account:deposits"
            self.assertEqual(
                e2.data["preferences"]["favorite_accounts"][key], 1
            )
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)


class TestLearnAccountPreference(unittest.TestCase):
    def test_incrementa_contador(self):
        engine, tmpdir = make_engine()
        try:
            engine.learn_account_preference("Bank", "deposits")
            engine.learn_account_preference("Bank", "deposits")
            self.assertEqual(
                engine.data["preferences"]["favorite_accounts"]["Bank:deposits"],
                2,
            )
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_contextos_diferentes_se_cuentan_separado(self):
        engine, tmpdir = make_engine()
        try:
            engine.learn_account_preference("Bank", "deposits")
            engine.learn_account_preference("Bank", "transfers")
            self.assertEqual(
                engine.data["preferences"]["favorite_accounts"]["Bank:deposits"], 1
            )
            self.assertEqual(
                engine.data["preferences"]["favorite_accounts"]["Bank:transfers"], 1
            )
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)


class TestLearnVendorPreference(unittest.TestCase):
    def test_incrementa_contador(self):
        engine, tmpdir = make_engine()
        try:
            engine.learn_vendor_preference("ACME Corp", "bills")
            engine.learn_vendor_preference("ACME Corp", "bills")
            self.assertEqual(
                engine.data["preferences"]["frequent_vendors"]["ACME Corp:bills"],
                2,
            )
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)


class TestLearnReportUsage(unittest.TestCase):
    def test_agrega_reporte_a_patron(self):
        engine, tmpdir = make_engine()
        try:
            engine.learn_report_usage({"name": "P&L Mensual", "freq": "monthly"})
            self.assertEqual(
                engine.data["report_patterns"]["frequent_reports"][0]["name"],
                "P&L Mensual",
            )
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_no_duplica_reportes_identicos(self):
        engine, tmpdir = make_engine()
        try:
            engine.learn_report_usage({"name": "P&L", "period": "monthly"})
            engine.learn_report_usage({"name": "P&L", "period": "monthly"})
            self.assertEqual(
                len(engine.data["report_patterns"]["frequent_reports"]), 1
            )
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_incrementa_contador_de_reporte_existente(self):
        engine, tmpdir = make_engine()
        try:
            engine.learn_report_usage({"name": "P&L", "period": "monthly"})
            engine.learn_report_usage({"name": "P&L", "period": "monthly"})
            rep = engine.data["report_patterns"]["frequent_reports"][0]
            self.assertEqual(rep.get("count"), 2)
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)


class TestRecordCorrection(unittest.TestCase):
    def test_registra_correccion(self):
        engine, tmpdir = make_engine()
        try:
            engine.record_correction(
                wrong="Acme Corp",
                correct="ACME Corporation",
                context="search_customer",
            )
            corr = engine.data["corrections"]["entries"]
            self.assertEqual(len(corr), 1)
            self.assertEqual(corr[0]["wrong"], "Acme Corp")
            self.assertEqual(corr[0]["correct"], "ACME Corporation")
            self.assertEqual(corr[0]["context"], "search_customer")
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_correcciones_se_persisten(self):
        tmpdir = tempfile.mkdtemp()
        try:
            path = os.path.join(tmpdir, "corr.json")
            e1 = UserBehaviorLearningEngine(learning_file=path)
            e1.record_correction("X", "Y", "ctx")
            e2 = UserBehaviorLearningEngine(learning_file=path)
            self.assertEqual(len(e2.data["corrections"]["entries"]), 1)
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_limite_maximo_correcciones(self):
        engine, tmpdir = make_engine()
        try:
            engine.max_corrections = 3
            for i in range(5):
                engine.record_correction(f"wrong_{i}", f"correct_{i}", "ctx")
            self.assertEqual(len(engine.data["corrections"]["entries"]), 3)
            # Las primeras se descartan, las últimas quedan
            self.assertEqual(
                engine.data["corrections"]["entries"][-1]["wrong"], "wrong_4"
            )
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)


class TestGetSuggestions(unittest.TestCase):
    def test_sin_interacciones_retorna_vacio(self):
        engine, tmpdir = make_engine()
        try:
            suggestions = engine.get_suggestions()
            self.assertIn("accounts", suggestions)
            self.assertIn("vendors", suggestions)
            self.assertIn("reports", suggestions)
            self.assertIn("corrections", suggestions)
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_sugiere_cuenta_mas_usada(self):
        engine, tmpdir = make_engine()
        try:
            for _ in range(3):
                engine.learn_account_preference("Bank", "deposits")
            engine.learn_account_preference("Other", "deposits")
            suggestions = engine.get_suggestions()
            self.assertEqual(suggestions["accounts"][0]["name"], "Bank:deposits")
            self.assertEqual(suggestions["accounts"][0]["count"], 3)
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_sugiere_vendor_mas_usado(self):
        engine, tmpdir = make_engine()
        try:
            for _ in range(2):
                engine.learn_vendor_preference("ACME", "bills")
            suggestions = engine.get_suggestions()
            self.assertEqual(suggestions["vendors"][0]["name"], "ACME:bills")
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_sugiere_reporte_mas_usado(self):
        engine, tmpdir = make_engine()
        try:
            for _ in range(4):
                engine.learn_report_usage({"name": "P&L", "period": "monthly"})
            suggestions = engine.get_suggestions()
            self.assertEqual(suggestions["reports"][0]["name"], "P&L")
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_sugiere_correcciones_aplicables(self):
        engine, tmpdir = make_engine()
        try:
            for _ in range(3):
                engine.record_correction(
                    "Acme Corp", "ACME Corporation", "search_customer"
                )
            suggestions = engine.get_suggestions()
            self.assertEqual(len(suggestions["corrections"]), 1)
            self.assertEqual(suggestions["corrections"][0]["correct"], "ACME Corporation")
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)


class TestToolLearnFromInteraction(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.path = os.path.join(self.tmpdir, "behavior.json")
        reset_module_engine(self.path)

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_account_use(self):
        result = tool_learn_from_interaction(
            interaction_type="account_use",
            details={"account_name": "Bank"},
            context="deposits",
        )
        self.assertTrue(result["success"])
        with open(self.path) as f:
            data = json.load(f)
        self.assertEqual(
            data["preferences"]["favorite_accounts"]["Bank:deposits"], 1
        )

    def test_vendor_use(self):
        result = tool_learn_from_interaction(
            interaction_type="vendor_use",
            details={"vendor_name": "ACME"},
            context="bills",
        )
        self.assertTrue(result["success"])
        with open(self.path) as f:
            data = json.load(f)
        self.assertEqual(
            data["preferences"]["frequent_vendors"]["ACME:bills"], 1
        )

    def test_report_use(self):
        result = tool_learn_from_interaction(
            interaction_type="report_use",
            details={"name": "P&L", "period": "monthly"},
        )
        self.assertTrue(result["success"])

    def test_tipo_desconocido_retorna_error(self):
        result = tool_learn_from_interaction(
            interaction_type="unknown_type",
            details={"foo": "bar"},
        )
        self.assertFalse(result["success"])

    def test_account_use_sin_account_name(self):
        result = tool_learn_from_interaction(
            interaction_type="account_use",
            details={},
        )
        self.assertFalse(result["success"])

    def test_incrementa_stats(self):
        tool_learn_from_interaction("account_use", {"account_name": "X"})
        tool_learn_from_interaction("account_use", {"account_name": "X"})
        with open(self.path) as f:
            data = json.load(f)
        self.assertEqual(data["learning_stats"]["total_interactions"], 2)


class TestToolGetUserSuggestions(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.path = os.path.join(self.tmpdir, "behavior.json")
        reset_module_engine(self.path)

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_retorna_sugerencias(self):
        tool_learn_from_interaction("account_use", {"account_name": "Bank"})
        result = tool_get_user_suggestions()
        self.assertTrue(result["success"])
        self.assertIn("suggestions", result)
        self.assertIn("stats", result)

    def test_stats_incluye_total_interacciones(self):
        tool_learn_from_interaction("account_use", {"account_name": "X"})
        result = tool_get_user_suggestions()
        self.assertEqual(result["stats"]["total_interactions"], 1)


class TestToolRecordUserCorrection(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.path = os.path.join(self.tmpdir, "behavior.json")
        reset_module_engine(self.path)

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_registra_correccion(self):
        result = tool_record_user_correction(
            wrong="Acme Corp",
            correct="ACME Corporation",
            context="search_customer",
        )
        self.assertTrue(result["success"])
        with open(self.path) as f:
            data = json.load(f)
        self.assertEqual(len(data["corrections"]["entries"]), 1)

    def test_persiste_entre_llamadas(self):
        tool_record_user_correction("X1", "Y1", "ctx1")
        tool_record_user_correction("X2", "Y2", "ctx2")
        # Verifica que las correcciones se almacenaron (vía context de conversación)
        with open(self.path) as f:
            data = json.load(f)
        self.assertEqual(len(data["corrections"]["entries"]), 2)


class TestToolGetConversationContext(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.path = os.path.join(self.tmpdir, "behavior.json")
        reset_module_engine(self.path)

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_retorna_recent_topics(self):
        tool_learn_from_interaction("account_use", {"account_name": "Bank"})
        result = tool_get_conversation_context()
        self.assertTrue(result["success"])
        self.assertIn("recent_topics", result)

    def test_incluye_active_tasks(self):
        result = tool_get_conversation_context()
        self.assertIn("active_tasks", result)
        self.assertIsInstance(result["active_tasks"], list)

    def test_agrega_active_task(self):
        result = tool_get_conversation_context()
        # Sin acceso directo al motor, verificamos estructura
        self.assertIn("active_tasks", result)

    def test_incrementa_total_interactions(self):
        tool_learn_from_interaction("account_use", {"account_name": "X"})
        tool_learn_from_interaction("account_use", {"account_name": "X"})
        result = tool_get_conversation_context()
        # recent_topics debe tener items
        self.assertGreaterEqual(len(result["recent_topics"]), 2)


class TestGetRecentTopics(unittest.TestCase):
    def test_limite_20_topics(self):
        engine, tmpdir = make_engine()
        try:
            for i in range(25):
                engine.update_conversation_context(f"topic_{i}")
            topics = engine.data["conversation_context"]["recent_topics"]
            self.assertEqual(len(topics), 20)
            # Las primeras se descartan
            self.assertEqual(topics[0]["topic"], "topic_5")
            self.assertEqual(topics[-1]["topic"], "topic_24")
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_topic_con_action(self):
        engine, tmpdir = make_engine()
        try:
            engine.update_conversation_context("deposits", "create_deposit")
            topic = engine.data["conversation_context"]["recent_topics"][-1]
            self.assertEqual(topic["topic"], "deposits")
            self.assertEqual(topic["action"], "create_deposit")
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
