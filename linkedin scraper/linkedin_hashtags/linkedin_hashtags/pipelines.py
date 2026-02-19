# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import json
import csv
from datetime import datetime
from pathlib import Path
from itemadapter import ItemAdapter
from .items import HashtagItem


class HashtagValidationPipeline:
    """Validate and clean hashtag items"""
    
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        # Validate required fields
        if not adapter.get('name'):
            raise ValueError(f"Missing hashtag name: {item}")
            
        # Clean and normalize hashtag name
        hashtag_name = adapter['name'].strip().lower()
        if len(hashtag_name) < 2:
            raise ValueError(f"Hashtag name too short: {hashtag_name}")
            
        adapter['name'] = hashtag_name
        
        # Ensure mentions is an integer
        try:
            adapter['mentions'] = int(adapter.get('mentions', 0))
        except (ValueError, TypeError):
            adapter['mentions'] = 1
            
        return item


class JsonExportPipeline:
    """Export hashtags to JSON file"""
    
    def __init__(self):
        self.items = []
        
    def process_item(self, item, spider):
        self.items.append(ItemAdapter(item).asdict())
        return item
        
    def close_spider(self, spider):
        # Create output directory
        output_dir = Path('output')
        output_dir.mkdir(exist_ok=True)
        
        # Save JSON file with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        json_file = output_dir / f'linkedin_hashtags_{timestamp}.json'
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.items, f, indent=2, ensure_ascii=False)
            
        spider.logger.info(f"💾 Exported {len(self.items)} hashtags to {json_file}")


class CsvExportPipeline:
    """Export hashtags to CSV file"""
    
    def __init__(self):
        self.items = []
        
    def process_item(self, item, spider):
        self.items.append(ItemAdapter(item).asdict())
        return item
        
    def close_spider(self, spider):
        if not self.items:
            return
            
        # Create output directory
        output_dir = Path('output')
        output_dir.mkdir(exist_ok=True)
        
        # Save CSV file with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_file = output_dir / f'linkedin_hashtags_{timestamp}.csv'
        
        # Get field names from first item
        fieldnames = self.items[0].keys()
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.items)
            
        spider.logger.info(f"📊 Exported {len(self.items)} hashtags to {csv_file}")


class ReportPipeline:
    """Generate a summary report"""
    
    def __init__(self):
        self.items = []
        
    def process_item(self, item, spider):
        self.items.append(ItemAdapter(item).asdict())
        return item
        
    def close_spider(self, spider):
        if not self.items:
            spider.logger.info("📄 No hashtags found for report")
            return
            
        # Sort by mentions count
        sorted_items = sorted(self.items, key=lambda x: x['mentions'], reverse=True)
        
        # Generate report
        total_hashtags = len(sorted_items)
        total_mentions = sum(item['mentions'] for item in sorted_items)
        
        report_lines = [
            "\n" + "="*60,
            f"🏷️  LinkedIn Hashtags Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "="*60,
            f"📊 Total unique hashtags found: {total_hashtags}",
            f"📈 Total mentions across all hashtags: {total_mentions}",
            "",
            "🔥 Top 15 Trending Hashtags:",
            "-"*40
        ]
        
        for i, item in enumerate(sorted_items[:15], 1):
            mentions = item['mentions']
            hashtag = item['original_case']
            emoji = '🚀' if mentions > 5 else '⭐' if mentions > 2 else '📌'
            
            report_lines.append(
                f"{i:2d}. #{hashtag} ({mentions} mentions) {emoji}"
            )
            
        report_lines.extend(["", "="*60])
        
        report = "\n".join(report_lines)
        print(report)
        
        # Save report to file
        output_dir = Path('output')
        output_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = output_dir / f'hashtags_report_{timestamp}.txt'
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
            
        spider.logger.info(f"📋 Generated report: {report_file}")
