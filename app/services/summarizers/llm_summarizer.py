"""LLM-based activity summarization service."""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Callable, AsyncGenerator
from sqlalchemy.orm import Session
from sqlalchemy import func
from openai import OpenAI
import httpx
import asyncio
import json
from app.models.member import Activity, Summary, Member
from app.core.config.settings import settings


class LLMSummarizer:
    """LLM-based summarization service."""
    
    def __init__(self, db: Session):
        self.db = db
        self.client = None
        if settings.openai_api_key:
            self.client = OpenAI(
                api_key=settings.openai_api_key,
                base_url=settings.openai_base_url
            )
    
    def can_summarize(self) -> bool:
        """Check if LLM summarization is available."""
        return self.client is not None and settings.openai_api_key is not None
    
    async def generate_daily_summary(self, date: Optional[datetime] = None) -> Optional[Summary]:
        """Generate daily activity summary."""
        if not self.can_summarize():
            return None
        
        if date is None:
            date = datetime.utcnow().date()
        
        start_date = datetime.combine(date, datetime.min.time())
        end_date = datetime.combine(date, datetime.max.time())
        
        activities = self._get_activities_in_range(start_date, end_date)
        
        if not activities:
            return None
        
        summary_content = await self._generate_summary_content(
            activities, "daily", start_date, end_date
        )
        
        if not summary_content:
            return None
        
        # Create summary record with bilingual content
        summary = Summary(
            title=f"Daily Activity Summary - {date.strftime('%Y-%m-%d')}",
            content=summary_content["chinese"],
            content_en=summary_content["english"],
            summary_type="daily",
            start_date=start_date,
            end_date=end_date,
            member_count=len(set(activity.member_id for activity in activities)),
            activity_count=len(activities)
        )
        
        self.db.add(summary)
        self.db.commit()
        self.db.refresh(summary)
        
        return summary
    
    async def generate_weekly_summary(self, start_date: Optional[datetime] = None) -> Optional[Summary]:
        """Generate weekly activity summary."""
        if not self.can_summarize():
            return None
        
        if start_date is None:
            # Start from Monday of current week
            today = datetime.utcnow().date()
            start_date = today - timedelta(days=today.weekday())
        
        end_date = start_date + timedelta(days=6)
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.max.time())
        
        activities = self._get_activities_in_range(start_datetime, end_datetime)
        
        if not activities:
            return None
        
        summary_content = await self._generate_summary_content(
            activities, "weekly", start_datetime, end_datetime
        )
        
        if not summary_content:
            return None
        
        # Create summary record with bilingual content
        summary = Summary(
            title=f"Weekly Activity Summary - {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
            content=summary_content["chinese"],
            content_en=summary_content["english"],
            summary_type="weekly",
            start_date=start_datetime,
            end_date=end_datetime,
            member_count=len(set(activity.member_id for activity in activities)),
            activity_count=len(activities)
        )
        
        self.db.add(summary)
        self.db.commit()
        self.db.refresh(summary)
        
        return summary
    
    async def generate_custom_summary(
        self, 
        start_date: datetime, 
        end_date: datetime,
        title: str
    ) -> Optional[Summary]:
        """Generate custom date range summary."""
        if not self.can_summarize():
            return None
        
        activities = self._get_activities_in_range(start_date, end_date)
        
        if not activities:
            return None
        
        summary_content = await self._generate_summary_content(
            activities, "custom", start_date, end_date
        )
        
        if not summary_content:
            return None
        
        # Create summary record with bilingual content
        summary = Summary(
            title=title,
            content=summary_content["chinese"],
            content_en=summary_content["english"],
            summary_type="custom",
            start_date=start_date,
            end_date=end_date,
            member_count=len(set(activity.member_id for activity in activities)),
            activity_count=len(activities)
        )
        
        self.db.add(summary)
        self.db.commit()
        self.db.refresh(summary)
        
        return summary
    
    def _get_activities_in_range(self, start_date: datetime, end_date: datetime) -> List[Activity]:
        """Get activities within the specified date range."""
        return self.db.query(Activity).filter(
            Activity.created_at >= start_date,
            Activity.created_at <= end_date
        ).order_by(Activity.created_at.desc()).all()
    
    async def _generate_summary_content(
        self, 
        activities: List[Activity], 
        summary_type: str,
        start_date: datetime,
        end_date: datetime
    ) -> Optional[Dict[str, str]]:
        """Generate bilingual summary content using LLM."""
        if not activities:
            return None
        
        # Group activities by member
        activities_by_member = {}
        for activity in activities:
            member_id = activity.member_id
            if member_id not in activities_by_member:
                activities_by_member[member_id] = []
            activities_by_member[member_id].append(activity)
        
        # Prepare activity data for LLM
        activity_data = []
        for member_id, member_activities in activities_by_member.items():
            member = self.db.query(Member).filter(Member.id == member_id).first()
            if member:
                member_activity_summary = {
                    "member_name": member.name,
                    "member_position": member.position,
                    "activities": []
                }
                
                for activity in member_activities:
                    member_activity_summary["activities"].append({
                        "platform": activity.platform,
                        "type": activity.activity_type,
                        "title": activity.title,
                        "content": activity.content,
                        "url": activity.url,
                        "published_at": activity.published_at.isoformat() if activity.published_at else None
                    })
                
                activity_data.append(member_activity_summary)
        
        # Generate Chinese content
        chinese_content = await self._generate_language_content(
            activity_data, summary_type, start_date, end_date, "chinese"
        )
        
        # Generate English content
        english_content = await self._generate_language_content(
            activity_data, summary_type, start_date, end_date, "english"
        )
        
        if not chinese_content or not english_content:
            return None
        
        return {
            "chinese": chinese_content,
            "english": english_content
        }
    
    def _create_summary_prompt(
        self, 
        activity_data: List[Dict], 
        summary_type: str,
        start_date: datetime,
        end_date: datetime
    ) -> str:
        """Create prompt for LLM summarization."""
        
        date_range = f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
        
        prompt = f"""
Please create a {summary_type} summary of team member social media activities for the period {date_range}.

Activity Data:
{self._format_activity_data(activity_data)}

Please provide a comprehensive summary that includes:
1. Overall activity overview and trends
2. Key highlights from each team member
3. Platform-specific insights (LinkedIn, GitHub, etc.)
4. Notable achievements or milestones
5. Recommendations or observations

**IMPORTANT**: Format the summary in Markdown format with proper headings, bullet points, and formatting. Use:
- `#` for main headings
- `##` for subheadings
- `###` for section headings
- `-` for bullet points
- `**bold**` for emphasis
- `*italic*` for secondary emphasis
- Code blocks with ``` for any technical content
- Tables with | for structured data

Make it professional, well-structured, and easy to read with clear sections and proper Markdown formatting.
"""
        
        return prompt

    async def _generate_language_content(
        self,
        activity_data: List[Dict],
        summary_type: str,
        start_date: datetime,
        end_date: datetime,
        language: str
    ) -> Optional[str]:
        """Generate content in specific language."""
        date_range = f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
        
        if language == "chinese":
            system_prompt = "你是一位专业的社交媒体活动分析师。请为团队成员在各种平台上的活动创建简洁、信息丰富的总结报告。请用中文回答。"
            prompt = f"""
请为{date_range}期间的团队成员社交媒体活动创建{summary_type}总结报告。

活动数据：
{self._format_activity_data(activity_data)}

请提供包含以下内容的综合总结：
1. 整体活动概览和趋势
2. 每位团队成员的关键亮点
3. 平台特定洞察（LinkedIn、GitHub等）
4. 值得注意的成就或里程碑
5. 建议或观察

**重要**：请使用Markdown格式，包含适当的标题、项目符号和格式。使用：
- `#` 作为主标题
- `##` 作为副标题
- `###` 作为章节标题
- `-` 作为项目符号
- `**粗体**` 用于强调
- `*斜体*` 用于次要强调
- 使用 ``` 的代码块用于任何技术内容
- 使用 | 的表格用于结构化数据

使其专业、结构良好且易于阅读，具有清晰的章节和适当的Markdown格式。
"""
        else:  # english
            system_prompt = "You are a professional social media activity analyst. Create concise, informative summaries of team member activities across various platforms."
            prompt = f"""
Please create a {summary_type} summary of team member social media activities for the period {date_range}.

Activity Data:
{self._format_activity_data(activity_data)}

Please provide a comprehensive summary that includes:
1. Overall activity overview and trends
2. Key highlights from each team member
3. Platform-specific insights (LinkedIn, GitHub, etc.)
4. Notable achievements or milestones
5. Recommendations or observations

**IMPORTANT**: Format the summary in Markdown format with proper headings, bullet points, and formatting. Use:
- `#` for main headings
- `##` for subheadings
- `###` for section headings
- `-` for bullet points
- `**bold**` for emphasis
- `*italic*` for secondary emphasis
- Code blocks with ``` for any technical content
- Tables with | for structured data

Make it professional, well-structured, and easy to read with clear sections and proper Markdown formatting.
"""
        
        try:
            if "dashscope.aliyuncs.com" in settings.openai_base_url:
                # 阿里云通义千问
                headers = {
                    "Authorization": f"Bearer {settings.openai_api_key}",
                    "Content-Type": "application/json"
                }
                data = {
                    "model": settings.openai_model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": 2000,
                    "temperature": 0.7
                }
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        settings.openai_base_url,
                        headers=headers,
                        json=data,
                        timeout=30.0
                    )
                    if response.status_code == 200:
                        result = response.json()
                        return result["choices"][0]["message"]["content"]
                    else:
                        print(f"Aliyun API error: {response.status_code} {response.text}")
                        return None
            else:
                response = self.client.chat.completions.create(
                    model=settings.openai_model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=2000,
                    temperature=0.7
                )
                return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error generating {language} LLM summary: {e}")
            return None

    async def _generate_language_content_stream(
        self,
        activity_data: List[Dict],
        summary_type: str,
        start_date: datetime,
        end_date: datetime,
        language: str,
        progress_callback: Optional[Callable[[str, str], None]] = None
    ) -> Optional[str]:
        """Generate content in specific language with streaming support."""
        date_range = f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
        
        if language == "chinese":
            system_prompt = "你是一位专业的社交媒体活动分析师。请为团队成员在各种平台上的活动创建简洁、信息丰富的总结报告。请用中文回答。"
            prompt = f"""
请为{date_range}期间的团队成员社交媒体活动创建{summary_type}总结报告。

活动数据：
{self._format_activity_data(activity_data)}

请提供包含以下内容的综合总结：
1. 整体活动概览和趋势
2. 每位团队成员的关键亮点
3. 平台特定洞察（LinkedIn、GitHub等）
4. 值得注意的成就或里程碑
5. 建议或观察

**重要**：请使用Markdown格式，包含适当的标题、项目符号和格式。使用：
- `#` 作为主标题
- `##` 作为副标题
- `###` 作为章节标题
- `-` 作为项目符号
- `**粗体**` 用于强调
- `*斜体*` 用于次要强调
- 使用 ``` 的代码块用于任何技术内容
- 使用 | 的表格用于结构化数据

使其专业、结构良好且易于阅读，具有清晰的章节和适当的Markdown格式。
"""
        else:  # english
            system_prompt = "You are a professional social media activity analyst. Create concise, informative summaries of team member activities across various platforms."
            prompt = f"""
Please create a {summary_type} summary of team member social media activities for the period {date_range}.

Activity Data:
{self._format_activity_data(activity_data)}

Please provide a comprehensive summary that includes:
1. Overall activity overview and trends
2. Key highlights from each team member
3. Platform-specific insights (LinkedIn, GitHub, etc.)
4. Notable achievements or milestones
5. Recommendations or observations

**IMPORTANT**: Format the summary in Markdown format with proper headings, bullet points, and formatting. Use:
- `#` for main headings
- `##` for subheadings
- `###` for section headings
- `-` for bullet points
- `**bold**` for emphasis
- `*italic*` for secondary emphasis
- Code blocks with ``` for any technical content
- Tables with | for structured data

Make it professional, well-structured, and easy to read with clear sections and proper Markdown formatting.
"""
        
        try:
            if "dashscope.aliyuncs.com" in settings.openai_base_url:
                # 阿里云通义千问 - 支持流式
                headers = {
                    "Authorization": f"Bearer {settings.openai_api_key}",
                    "Content-Type": "application/json"
                }
                data = {
                    "model": settings.openai_model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": 2000,
                    "temperature": 0.7,
                    "stream": True
                }
                
                content = ""
                async with httpx.AsyncClient() as client:
                    async with client.stream(
                        "POST",
                        settings.openai_base_url,
                        headers=headers,
                        json=data,
                        timeout=60.0
                    ) as response:
                        if response.status_code == 200:
                            async for line in response.aiter_lines():
                                if line.startswith("data: "):
                                    data_line = line[6:]
                                    if data_line.strip() == "[DONE]":
                                        break
                                    try:
                                        chunk = json.loads(data_line)
                                        if "choices" in chunk and len(chunk["choices"]) > 0:
                                            delta = chunk["choices"][0].get("delta", {})
                                            if "content" in delta:
                                                content += delta["content"]
                                                # 实时回调内容更新
                                                if progress_callback:
                                                    progress_callback("content", delta["content"])

                                    except json.JSONDecodeError:
                                        continue
                            return content
                        else:
                            print(f"Aliyun API error: {response.status_code}")
                            return None
            else:
                # OpenAI - 支持流式
                content = ""
                stream = self.client.chat.completions.create(
                    model=settings.openai_model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=2000,
                    temperature=0.7,
                    stream=True
                )
                
                for chunk in stream:
                    if chunk.choices[0].delta.content is not None:
                        content += chunk.choices[0].delta.content
                        # 实时回调内容更新
                        if progress_callback:
                            progress_callback("content", chunk.choices[0].delta.content)

                
                return content
            
        except Exception as e:
            print(f"Error generating {language} LLM summary: {e}")
            return None

    async def _generate_language_content_stream_generator(
        self,
        activity_data: List[Dict],
        summary_type: str,
        start_date: datetime,
        end_date: datetime,
        language: str
    ) -> AsyncGenerator[str, None]:
        """Generate content in specific language with streaming generator."""
        date_range = f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
        
        if language == "chinese":
            system_prompt = "你是一位专业的社交媒体活动分析师。请为团队成员在各种平台上的活动创建简洁、信息丰富的总结报告。请用中文回答。"
            prompt = f"""
请为{date_range}期间的团队成员社交媒体活动创建{summary_type}总结报告。

活动数据：
{self._format_activity_data(activity_data)}

请提供包含以下内容的综合总结：
1. 整体活动概览和趋势
2. 每位团队成员的关键亮点
3. 平台特定洞察（LinkedIn、GitHub等）
4. 值得注意的成就或里程碑
5. 建议或观察

**重要**：请使用Markdown格式，包含适当的标题、项目符号和格式。使用：
- `#` 作为主标题
- `##` 作为副标题
- `###` 作为章节标题
- `-` 作为项目符号
- `**粗体**` 用于强调
- `*斜体*` 用于次要强调
- 使用 ``` 的代码块用于任何技术内容
- 使用 | 的表格用于结构化数据

使其专业、结构良好且易于阅读，具有清晰的章节和适当的Markdown格式。
"""
        else:  # english
            system_prompt = "You are a professional social media activity analyst. Create concise, informative summaries of team member activities across various platforms."
            prompt = f"""
Please create a {summary_type} summary of team member social media activities for the period {date_range}.

Activity Data:
{self._format_activity_data(activity_data)}

Please provide a comprehensive summary that includes:
1. Overall activity overview and trends
2. Key highlights from each team member
3. Platform-specific insights (LinkedIn, GitHub, etc.)
4. Notable achievements or milestones
5. Recommendations or observations

**IMPORTANT**: Format the summary in Markdown format with proper headings, bullet points, and formatting. Use:
- `#` for main headings
- `##` for subheadings
- `###` for section headings
- `-` for bullet points
- `**bold**` for emphasis
- `*italic*` for secondary emphasis
- Code blocks with ``` for any technical content
- Tables with | for structured data

Make it professional, well-structured, and easy to read with clear sections and proper Markdown formatting.
"""
        
        try:
            if "dashscope.aliyuncs.com" in settings.openai_base_url:
                # 阿里云通义千问 - 支持流式
                headers = {
                    "Authorization": f"Bearer {settings.openai_api_key}",
                    "Content-Type": "application/json"
                }
                data = {
                    "model": settings.openai_model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": 2000,
                    "temperature": 0.7,
                    "stream": True
                }
                
                async with httpx.AsyncClient() as client:
                    async with client.stream(
                        "POST",
                        settings.openai_base_url,
                        headers=headers,
                        json=data,
                        timeout=60.0
                    ) as response:
                        if response.status_code == 200:
                            async for line in response.aiter_lines():
                                if line.startswith("data: "):
                                    data_line = line[6:]
                                    if data_line.strip() == "[DONE]":
                                        break
                                    try:
                                        chunk = json.loads(data_line)
                                        if "choices" in chunk and len(chunk["choices"]) > 0:
                                            delta = chunk["choices"][0].get("delta", {})
                                            if "content" in delta:
                                                yield delta["content"]
                                    except json.JSONDecodeError:
                                        continue
                        else:
                            yield f"Error: API returned status {response.status_code}"
            else:
                # OpenAI - 支持流式
                stream = self.client.chat.completions.create(
                    model=settings.openai_model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=2000,
                    temperature=0.7,
                    stream=True
                )
                
                for chunk in stream:
                    if chunk.choices[0].delta.content is not None:
                        yield chunk.choices[0].delta.content
            
        except Exception as e:
            yield f"Error generating {language} LLM summary: {e}"
    
    def _format_activity_data(self, activity_data: List[Dict]) -> str:
        """Format activity data for LLM prompt."""
        formatted = ""
        
        for member_data in activity_data:
            formatted += f"\n{member_data['member_name']} ({member_data['member_position']}):\n"
            
            for activity in member_data['activities']:
                formatted += f"- {activity['platform'].upper()}: {activity['type']}"
                if activity['title']:
                    formatted += f" - {activity['title']}"
                if activity['content']:
                    formatted += f"\n  Content: {activity['content'][:200]}..."
                formatted += "\n"
        
        return formatted

    async def generate_member_summary(
        self, 
        member_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        days: int = 7
    ) -> Optional[Summary]:
        """Generate summary for a specific member's activities."""
        if not self.can_summarize():
            return None
        
        # Set date range
        if end_date is None:
            end_date = datetime.utcnow()
        if start_date is None:
            start_date = end_date - timedelta(days=days)
        
        # Get member info
        member = self.db.query(Member).filter(Member.id == member_id).first()
        if not member:
            return None
        
        # Debug: Print date range
        print(f"Searching for activities between {start_date} and {end_date}")
        
        # Get activities for this member in the date range
        # First get all activities for the member, then filter by date
        all_activities = self.db.query(Activity).filter(
            Activity.member_id == member_id
        ).order_by(Activity.published_at.desc()).all()
        
        # Filter activities by date range
        activities = []
        for activity in all_activities:
            if activity.published_at and start_date <= activity.published_at <= end_date:
                activities.append(activity)
        
        print(f"Found {len(activities)} activities for member {member_id}")
        
        if not activities:
            return None
        
        # Generate bilingual summary content
        summary_content = await self._generate_member_summary_content(
            member, activities, start_date, end_date
        )
        
        if not summary_content:
            return None
        
        # Create summary record with bilingual content
        summary = Summary(
            title=f"{member.name} - Activity Summary ({start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')})",
            content=summary_content["chinese"],
            content_en=summary_content["english"],
            summary_type="member",
            start_date=start_date,
            end_date=end_date,
            member_count=1,
            activity_count=len(activities)
        )
        
        self.db.add(summary)
        self.db.commit()
        self.db.refresh(summary)
        
        return summary

    async def _generate_member_summary_content(
        self,
        member: Member,
        activities: List[Activity],
        start_date: datetime,
        end_date: datetime
    ) -> Optional[Dict[str, str]]:
        """Generate bilingual summary content for a specific member."""
        if not activities:
            return None
        
        # Prepare activity data for LLM
        activity_data = []
        for activity in activities:
            activity_data.append({
                "platform": activity.platform,
                "type": activity.activity_type,
                "title": activity.title,
                "content": activity.content,
                "url": activity.url,
                "published_at": activity.published_at.isoformat() if activity.published_at else None,
                "created_at": activity.created_at.isoformat()
            })
        
        # Generate Chinese content
        chinese_content = await self._generate_member_language_content(
            member, activity_data, start_date, end_date, "chinese"
        )
        
        # Generate English content
        english_content = await self._generate_member_language_content(
            member, activity_data, start_date, end_date, "english"
        )
        
        if not chinese_content or not english_content:
            return None
        
        return {
            "chinese": chinese_content,
            "english": english_content
        }

    async def _generate_member_language_content(
        self,
        member: Member,
        activity_data: List[Dict],
        start_date: datetime,
        end_date: datetime,
        language: str
    ) -> Optional[str]:
        """Generate content in specific language for a member."""
        date_range = f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
        
        if language == "chinese":
            system_prompt = "你是一位专业的社交媒体活动分析师。请为团队成员在各种平台上的活动创建简洁、信息丰富的总结报告。请用中文回答。"
            prompt = f"""
请为{member.name}在{date_range}期间的社交媒体活动创建总结报告。

成员信息：
- 姓名：{member.name}
- 职位：{member.position or '未指定'}
- 部门：{member.department or '未指定'}

活动数据：
{self._format_member_activity_data(activity_data)}

请提供包含以下内容的综合总结：
1. 整体活动概览和参与度水平
2. 关键亮点和值得注意的活动
3. 平台特定洞察（LinkedIn、GitHub等）
4. 专业发展和成就
5. 在线存在趋势和模式
6. 建议或观察

**重要**：请使用Markdown格式，包含适当的标题、项目符号和格式。使用：
- `#` 作为主标题
- `##` 作为副标题
- `###` 作为章节标题
- `-` 作为项目符号
- `**粗体**` 用于强调
- `*斜体*` 用于次要强调
- 使用 ``` 的代码块用于任何技术内容
- 使用 | 的表格用于结构化数据

使其专业、结构良好且易于阅读，具有清晰的章节和适当的Markdown格式。保持简洁但信息丰富，重点关注其活动的最重要方面。
"""
        else:  # english
            system_prompt = "You are a professional social media activity analyst. Create concise, informative summaries of individual team member activities."
            prompt = f"""
Please create a summary of {member.name}'s social media activities for the period {date_range}.

Member Information:
- Name: {member.name}
- Position: {member.position or 'Not specified'}
- Department: {member.department or 'Not specified'}

Activity Data:
{self._format_member_activity_data(activity_data)}

Please provide a comprehensive summary that includes:
1. Overall activity overview and engagement level
2. Key highlights and notable activities
3. Platform-specific insights (LinkedIn, GitHub, etc.)
4. Professional development and achievements
5. Trends and patterns in their online presence
6. Recommendations or observations

**IMPORTANT**: Format the summary in Markdown format with proper headings, bullet points, and formatting. Use:
- `#` for main headings
- `##` for subheadings
- `###` for section headings
- `-` for bullet points
- `**bold**` for emphasis
- `*italic*` for secondary emphasis
- Code blocks with ``` for any technical content
- Tables with | for structured data

Make it professional, well-structured, and easy to read with clear sections and proper Markdown formatting. Keep it concise but informative, focusing on the most important aspects of their activities.
"""
        
        try:
            if "dashscope.aliyuncs.com" in settings.openai_base_url:
                headers = {
                    "Authorization": f"Bearer {settings.openai_api_key}",
                    "Content-Type": "application/json"
                }
                data = {
                    "model": settings.openai_model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": 2000,
                    "temperature": 0.7
                }
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        settings.openai_base_url,
                        headers=headers,
                        json=data,
                        timeout=30.0
                    )
                    if response.status_code == 200:
                        result = response.json()
                        return result["choices"][0]["message"]["content"]
                    else:
                        print(f"Aliyun API error: {response.status_code} {response.text}")
                        return None
            else:
                response = self.client.chat.completions.create(
                    model=settings.openai_model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=2000,
                    temperature=0.7
                )
                return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error generating {language} LLM summary for member {member.id}: {e}")
            return None

    def _create_member_summary_prompt(
        self,
        member: Member,
        activity_data: List[Dict],
        start_date: datetime,
        end_date: datetime
    ) -> str:
        """Create prompt for member-specific LLM summarization."""
        
        date_range = f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
        
        prompt = f"""
Please create a summary of {member.name}'s social media activities for the period {date_range}.

Member Information:
- Name: {member.name}
- Position: {member.position or 'Not specified'}
- Department: {member.department or 'Not specified'}

Activity Data:
{self._format_member_activity_data(activity_data)}

Please provide a comprehensive summary that includes:
1. Overall activity overview and engagement level
2. Key highlights and notable activities
3. Platform-specific insights (LinkedIn, GitHub, etc.)
4. Professional development and achievements
5. Trends and patterns in their online presence
6. Recommendations or observations

**IMPORTANT**: Format the summary in Markdown format with proper headings, bullet points, and formatting. Use:
- `#` for main headings
- `##` for subheadings
- `###` for section headings
- `-` for bullet points
- `**bold**` for emphasis
- `*italic*` for secondary emphasis
- Code blocks with ``` for any technical content
- Tables with | for structured data

Make it professional, well-structured, and easy to read with clear sections and proper Markdown formatting. Keep it concise but informative, focusing on the most important aspects of their activities.
"""
        
        return prompt

    def _format_member_activity_data(self, activity_data: List[Dict]) -> str:
        """Format activity data for member-specific LLM prompt."""
        formatted = ""
        
        for activity in activity_data:
            formatted += f"\n{activity['platform'].upper()} - {activity['type']}"
            if activity['title']:
                formatted += f"\nTitle: {activity['title']}"
            if activity['content']:
                formatted += f"\nContent: {activity['content'][:300]}..."
            if activity['published_at']:
                formatted += f"\nPublished: {activity['published_at']}"
            if activity['url']:
                formatted += f"\nURL: {activity['url']}"
            formatted += "\n" + "-" * 50 + "\n"
        
        return formatted 