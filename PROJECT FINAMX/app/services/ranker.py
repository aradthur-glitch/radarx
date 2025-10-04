from typing import List, Dict, Any
from datetime import datetime
import numpy as np
import yfinance as yf
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


class NewsRanker:
    def rank_clusters(self, clusters: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        ranked = []
        for cluster in clusters:
            hotness = self._calculate_hotness(cluster)
            ranked.append({'cluster': cluster, 'hotness': hotness})
        ranked = sorted(ranked, key=lambda x: x['hotness'], reverse=True)
        logger.info(f"🎯 Топ-кластеры ранжированы, макс hotness: {ranked[0]['hotness'] if ranked else 0}")
        return ranked

    def _calculate_hotness(self, cluster: Dict[str, Any]) -> float:
        cluster_list = cluster.get('cluster', [])
        if not cluster_list:
            return 0.0

        times = [news['published_at'] for news in cluster_list]
        time_delta = (max(times) - min(times)).total_seconds() / 3600 if times else 0
        velocity = len(cluster_list) / max(time_delta, 1)

        avg_sentiment = np.mean([news.get('sentiment', 0) for news in cluster_list])

        entities = cluster.get('entities', [])
        impact = 0.0
        if entities:
            ticker = entities[0]
            try:
                data = yf.Ticker(ticker).history(period='1d')
                if len(data) >= 2:
                    change = (data['Close'][-1] - data['Close'][-2]) / data['Close'][-2]
                    impact = abs(change)
            except:
                pass

        hotness = 0.5 * velocity / 10 + 0.3 * (avg_sentiment + 1) / 2 + 0.2 * impact
        return min(hotness, 1.0)
