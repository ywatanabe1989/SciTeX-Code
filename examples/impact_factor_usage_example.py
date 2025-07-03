#!/usr/bin/env python3
"""
Impact Factor Usage Example

This script demonstrates how to use the impact_factor package
for retrieving journal impact factors, even though the CLI
has dependency issues.
"""

import sqlite3
import pandas as pd
import impact_factor

def get_impact_factor_direct(journal_name, year=2022):
    """
    Get impact factor directly from the SQLite database.
    
    Args:
        journal_name (str): Name of the journal
        year (int): Year for impact factor (default 2022)
    
    Returns:
        dict: Impact factor information
    """
    db_path = impact_factor.DEFAULT_DB
    
    try:
        conn = sqlite3.connect(db_path)
        
        # Query the database for the journal
        query = """
        SELECT * FROM impact_factor 
        WHERE journal LIKE ? 
        AND year = ?
        ORDER BY impact_factor DESC
        LIMIT 10
        """
        
        results = pd.read_sql_query(
            query, 
            conn, 
            params=[f'%{journal_name}%', year]
        )
        
        conn.close()
        
        if len(results) > 0:
            return results.to_dict('records')
        else:
            return None
            
    except Exception as e:
        print(f"Error querying database: {e}")
        return None

def search_journals(keyword, limit=10):
    """
    Search for journals by keyword.
    
    Args:
        keyword (str): Search keyword
        limit (int): Maximum number of results
    
    Returns:
        pandas.DataFrame: Search results
    """
    db_path = impact_factor.DEFAULT_DB
    
    try:
        conn = sqlite3.connect(db_path)
        
        query = """
        SELECT journal, impact_factor, year, issn
        FROM impact_factor 
        WHERE journal LIKE ? 
        ORDER BY impact_factor DESC
        LIMIT ?
        """
        
        results = pd.read_sql_query(
            query, 
            conn, 
            params=[f'%{keyword}%', limit]
        )
        
        conn.close()
        return results
        
    except Exception as e:
        print(f"Error searching database: {e}")
        return pd.DataFrame()

def get_top_journals(field_keyword=None, limit=20):
    """
    Get top journals by impact factor.
    
    Args:
        field_keyword (str): Optional keyword to filter by field
        limit (int): Number of top journals to return
    
    Returns:
        pandas.DataFrame: Top journals
    """
    db_path = impact_factor.DEFAULT_DB
    
    try:
        conn = sqlite3.connect(db_path)
        
        if field_keyword:
            query = """
            SELECT journal, impact_factor, year, issn
            FROM impact_factor 
            WHERE journal LIKE ? 
            ORDER BY impact_factor DESC
            LIMIT ?
            """
            params = [f'%{field_keyword}%', limit]
        else:
            query = """
            SELECT journal, impact_factor, year, issn
            FROM impact_factor 
            ORDER BY impact_factor DESC
            LIMIT ?
            """
            params = [limit]
        
        results = pd.read_sql_query(query, conn, params=params)
        
        conn.close()
        return results
        
    except Exception as e:
        print(f"Error getting top journals: {e}")
        return pd.DataFrame()

def main():
    """Main function demonstrating usage."""
    print("Impact Factor Package Usage Examples")
    print("=" * 50)
    
    # Example 1: Search for specific journals
    print("\n1. Searching for 'Nature' journals:")
    nature_journals = search_journals("Nature", limit=5)
    if len(nature_journals) > 0:
        print(nature_journals.to_string(index=False))
    else:
        print("No results found")
    
    # Example 2: Get impact factor for a specific journal
    print("\n2. Getting impact factor for 'Science':")
    science_if = get_impact_factor_direct("Science")
    if science_if:
        for journal in science_if[:3]:  # Show top 3 matches
            print(f"  {journal.get('journal', 'N/A')}: IF = {journal.get('impact_factor', 'N/A')}")
    else:
        print("No results found")
    
    # Example 3: Top journals in neuroscience
    print("\n3. Top neuroscience journals:")
    neuro_journals = get_top_journals("neuroscience", limit=5)
    if len(neuro_journals) > 0:
        print(neuro_journals.to_string(index=False))
    else:
        print("No neuroscience journals found")
    
    # Example 4: Overall top journals
    print("\n4. Top 10 journals overall:")
    top_journals = get_top_journals(limit=10)
    if len(top_journals) > 0:
        print(top_journals.to_string(index=False))
    else:
        print("No results found")
    
    # Example 5: Database statistics
    print("\n5. Database statistics:")
    try:
        conn = sqlite3.connect(impact_factor.DEFAULT_DB)
        
        # Get total number of journals
        total_count = pd.read_sql_query(
            "SELECT COUNT(*) as count FROM impact_factor", 
            conn
        ).iloc[0]['count']
        
        # Get year range
        year_range = pd.read_sql_query(
            "SELECT MIN(year) as min_year, MAX(year) as max_year FROM impact_factor", 
            conn
        ).iloc[0]
        
        # Get impact factor range
        if_range = pd.read_sql_query(
            "SELECT MIN(impact_factor) as min_if, MAX(impact_factor) as max_if FROM impact_factor", 
            conn
        ).iloc[0]
        
        conn.close()
        
        print(f"  Total journals: {total_count}")
        print(f"  Year range: {year_range['min_year']} - {year_range['max_year']}")
        print(f"  Impact factor range: {if_range['min_if']:.3f} - {if_range['max_if']:.3f}")
        
    except Exception as e:
        print(f"  Error getting statistics: {e}")

if __name__ == "__main__":
    main()