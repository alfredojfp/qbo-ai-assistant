# -*- coding: utf-8 -*-
"""
NIVEL 1: WEB SEARCH TOOL
Permite al LLM buscar información en internet cuando no sabe algo
"""

import requests
from typing import List, Dict
import json

def search_web(query: str, max_results: int = 5) -> Dict:
    """
    Busca en internet usando DuckDuckGo (gratis, sin API key)

    Args:
        query: Consulta de búsqueda
        max_results: Número máximo de resultados

    Returns:
        dict con resultados
    """
    try:
        # DuckDuckGo Instant Answer API (gratis)
        url = "https://api.duckduckgo.com/"
        params = {
            'q': query,
            'format': 'json',
            'no_html': 1,
            'skip_disambig': 1
        }

        response = requests.get(url, params=params, timeout=10)

        if response.status_code != 200:
            return {
                "success": False,
                "error": f"Status code: {response.status_code}"
            }

        data = response.json()

        # Extraer resultados relevantes
        results = []

        # Abstract (respuesta directa)
        if data.get('Abstract'):
            results.append({
                'type': 'abstract',
                'title': data.get('Heading', ''),
                'snippet': data.get('Abstract', ''),
                'url': data.get('AbstractURL', '')
            })

        # Related topics
        for topic in data.get('RelatedTopics', [])[:max_results]:
            if 'Text' in topic:
                results.append({
                    'type': 'related',
                    'title': topic.get('Text', '').split(' - ')[0] if ' - ' in topic.get('Text', '') else '',
                    'snippet': topic.get('Text', ''),
                    'url': topic.get('FirstURL', '')
                })

        return {
            "success": True,
            "query": query,
            "results_count": len(results),
            "results": results
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def search_quickbooks_api_docs(query: str) -> Dict:
    """
    Búsqueda específica en documentación de QuickBooks API
    """
    search_query = f"QuickBooks Online API {query} site:developer.intuit.com"
    return search_web(search_query, max_results=3)


# Tool wrapper para el LLM
def tool_search_web(query: str) -> dict:
    """Tool: Busca información en internet"""
    return search_web(query)


def tool_search_qbo_docs(query: str) -> dict:
    """Tool: Busca en documentación de QuickBooks API"""
    return search_quickbooks_api_docs(query)
