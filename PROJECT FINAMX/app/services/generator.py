from typing import Dict, Any, List
from app.models.schemas import NewsEvent, Source, Timeline
from datetime import datetime
import openai
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

openai.api_key = settings.LLM_API_KEY


class DraftGenerator:
    async def generate_event(self, ranked_cluster: Dict[str, Any]) -> NewsEvent:
        cluster = ranked_cluster['cluster']['cluster']
        hotness = ranked_cluster['hotness']
        entities = ranked_cluster['cluster']['entities']

        prompt = f"""
        Создай финансовое событие на основе этих новостей:
        {', '.join([n['title'] for n in cluster[:3]])}
        Entities: {', '.join(entities[:5])}
        Why now? (кратко, 1-2 предложения). Headline: привлекательный заголовок.
        Верни JSON: {{"headline": "...", "why_now": "..."}} 
        """

        try:
            response = await openai.ChatCompletion.acreate(
                model=settings.LLM_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150
            )
            llm_text = response.choices[0].message.content
            draft = {"headline": "Generated Headline: Market Shift", "why_now": "Due to recent earnings."}
        except Exception as e:
            logger.error(f"LLM ошибка: {e}")
            draft = {"headline": cluster[0]['title'], "why_now": "Hot event detected"}

        sources = [Source(
            url=news['url'],
            source_name=news['source'],
            published_at=news['published_at'],
            type='original'
        ) for news in cluster]

        timeline = Timeline(
            first_mention=min(news['published_at'] for news in cluster),
            last_update=max(news['published_at'] for news in cluster)
        )

        return NewsEvent(
            headline=draft['headline'],
            hotness=hotness,
            why_now=draft['why_now'],
            entities=entities,
            sources=sources,
            timeline=timeline,
            draft=draft,
            dedup_group=ranked_cluster['cluster']['cluster_id']
        )
