from typing import List, Dict, Any
import spacy
from sentence_transformers import SentenceTransformer
from sklearn.cluster import DBSCAN
import re
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


class NewsProcessor:
    def __init__(self):
        self.sentence_model = SentenceTransformer(settings.SENTENCE_MODEL)
        try:
            self.nlp = spacy.load(settings.SPACY_MODEL)
        except OSError:
            logger.warning(
                f"⚠️ Модель spaCy '{settings.SPACY_MODEL}' не найдена. Установите: python -m spacy download {settings.SPACY_MODEL}")
            self.nlp = None

    def process_news(self, raw_news: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not raw_news:
            return []

        for news in raw_news:
            text = news.get('title', '') + ' ' + news.get('content', '')
            if self.nlp:
                doc = self.nlp(text)
                entities = [ent.text for ent in doc.ents if ent.label_ in ['ORG', 'MONEY', 'NORP',
                                                                           'PRODUCT']]  # NORP: Nationalities/religious groups (spaCy label)
                tickers = re.findall(r'\b[A-Z]{1,5}\b', text)
                entities.extend(tickers)
                news['entities'] = list(set(entities))
            else:
                tickers = re.findall(r'\b[A-Z]{1,5}\b', text)
                news['entities'] = list(set(tickers))

        texts = [news.get('title', '') + ' ' + news.get('summary', '') + ' ' + news.get('content', '')[:200] for news in
                 raw_news]
        embeddings = self.sentence_model.encode(texts)

        clustering = DBSCAN(eps=0.4, min_samples=2, metric='cosine').fit(embeddings)

        clusters = {}
        for idx, label in enumerate(clustering.labels_):  # type: ignore  # DBSCAN.labels_ from sklearn
            if label == -1:
                label = f"singleton_{idx}"
            if label not in clusters:
                clusters[label] = []
            clusters[label].append(raw_news[idx])

        processed_clusters = []
        for label, cluster in clusters.items():
            cluster_data = {
                'cluster_id': label,
                'size': len(cluster),
                'entities': list(set(ent for news in cluster for ent in news.get('entities', []))),
                'cluster': cluster
            }
            processed_clusters.append(cluster_data)

        logger.info(f"📦 Сформировано {len(processed_clusters)} кластеров из {len(raw_news)} новостей")
        return processed_clusters