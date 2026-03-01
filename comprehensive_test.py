#!/usr/bin/env python3
"""
Comprehensive Book Summarization Test
Tests the complete flow with multiple scenarios
"""
import requests
import json
import time
import random
import string

BASE_URL = "http://localhost:8000/api"

def random_username():
    """Generate a random username"""
    return "testuser_" + "".join(random.choices(string.ascii_lowercase + string.digits, k=6))

def test_single_book():
    """Test summarization of a single book"""
    print("\n" + "="*70)
    print("🧪 TEST: Single Book Summarization")
    print("="*70)
    
    username = random_username()
    
    # Register user
    print(f"\n1️⃣  Registering user: {username}")
    resp = requests.post(f"{BASE_URL}/auth/register", json={
        "username": username,
        "email": f"{username}@test.com",
        "password": "testpass123",
        "full_name": "Test User"
    })
    assert resp.status_code == 201, f"Registration failed: {resp.text}"
    user_data = resp.json()
    token = user_data["access_token"]
    print(f"   ✅ Registered and got token")
    
    # Upload book with file
    print(f"\n2️⃣  Uploading book with file...")
    book_text = """
    The Great Gatsby is a novel written by American author F. Scott Fitzgerald. 
    First published in 1925, the work is generally considered the greatest novel 
    of the Jazz Age. The story centers around Jay Gatsby, a mysterious millionaire 
    living in a mansion in Long Island, New York. The novel follows Nick Carraway 
    as he becomes drawn into the world of the wealthy elite and their complicated relationships.
    
    Set in the summer of 1922, the narrative explores themes of wealth, love, and 
    the American Dream. Gatsby's obsessive pursuit of his lost love, Daisy Buchanan, 
    drives much of the plot. Through their interactions and relationships with Tom Buchanan, 
    Daisy's husband, and Jordan Baker, the novel presents a complex portrait of the jazz age.
    
    Fitzgerald's prose is elegant and his characterization is detailed, making The Great 
    Gatsby a timeless work of literature that continues to be studied and celebrated in schools 
    and universities worldwide.
    """
    
    files = {
        'file': ('test_book.txt', book_text, 'text/plain')
    }
    data = {
        'title': 'The Great Gatsby',
        'author': 'F. Scott Fitzgerald',
        'isbn': '978-0-7432-7356-5',
        'description': 'A classic American novel'
    }
    headers = {'Authorization': f'Bearer {token}'}
    
    resp = requests.post(f"{BASE_URL}/books/", files=files, data=data, headers=headers)
    assert resp.status_code == 201, f"Book creation failed: {resp.text}"
    book = resp.json()
    book_id = book['id']
    print(f"   ✅ Book created: {book_id}")
    print(f"   📄 File URL: {book['file_url']}")
    print(f"   📋 File size: {book['file_size']} bytes")
    
    # Wait for summary
    print(f"\n3️⃣  Waiting for summary generation...")
    max_wait = 30
    for i in range(0, max_wait, 2):
        resp = requests.get(f"{BASE_URL}/books/{book_id}", headers=headers)
        assert resp.status_code == 200
        book = resp.json()
        metadata = book.get('metadata', {})
        summary = metadata.get('summary')
        
        if summary:
            print(f"   ✅ Summary generated in {i} seconds!")
            print(f"\n   📖 Summary preview:")
            print(f"   {summary[:200]}...")
            print(f"\n   🔍 Metadata:")
            print(f"   - Generated: {metadata.get('summary_generated_at')}")
            print(f"   - Model: {metadata.get('summary_model')}")
            return True
        
        print(f"   ⏳ Still waiting... ({i}s elapsed)")
        time.sleep(2)
    
    print(f"\n   ❌ Summary not generated after {max_wait}s")
    return False

def test_multiple_books():
    """Test summarization of multiple books"""
    print("\n" + "="*70)
    print("🧪 TEST: Multiple Books Summarization")
    print("="*70)
    
    username = random_username()
    
    # Register user
    print(f"\n1️⃣  Registering user: {username}")
    resp = requests.post(f"{BASE_URL}/auth/register", json={
        "username": username,
        "email": f"{username}@test.com",
        "password": "testpass123",
        "full_name": "Test User"
    })
    token = resp.json()["access_token"]
    print(f"   ✅ Registered")
    
    books = [
        {
            'title': 'Jane Eyre',
            'author': 'Charlotte Brontë',
            'text': 'Jane Eyre is a novel by Charlotte Brontë. The story follows Jane Eyre, an orphan girl who becomes a governess. She meets the mysterious Mr. Rochester and falls in love with him despite his dark secrets. The novel explores themes of love, morality, and independence. It is considered one of the great works of English literature.'
        },
        {
            'title': 'Pride and Prejudice',
            'author': 'Jane Austen',
            'text': 'Pride and Prejudice is a romantic novel by Jane Austen. The story centers on Elizabeth Bennet and Mr. Darcy. Initially prejudiced against each other, they gradually overcome their first impressions and fall in love. The novel satirizes social conventions and explores the nature of marriage and love in Regency-era England.'
        }
    ]
    
    book_ids = []
    print(f"\n2️⃣  Uploading {len(books)} books...")
    
    headers = {'Authorization': f'Bearer {token}'}
    
    for book_info in books:
        files = {
            'file': (f"{book_info['title']}.txt", book_info['text'], 'text/plain')
        }
        data = {
            'title': book_info['title'],
            'author': book_info['author']
        }
        
        resp = requests.post(f"{BASE_URL}/books/", files=files, data=data, headers=headers)
        assert resp.status_code == 201
        book = resp.json()
        book_ids.append(book['id'])
        print(f"   ✅ Uploaded: {book_info['title']}")
    
    # Check summaries
    print(f"\n3️⃣  Checking for summaries...")
    max_wait = 30
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        resp = requests.get(f"{BASE_URL}/books/", headers=headers)
        books_list = resp.json()['books']
        
        summaries_found = 0
        for book in books_list:
            if book.get('metadata', {}).get('summary'):
                summaries_found += 1
        
        print(f"   📊 Summaries found: {summaries_found}/{len(book_ids)}")
        
        if summaries_found == len(book_ids):
            print(f"   ✅ All summaries generated!")
            return True
        
        time.sleep(2)
    
    print(f"   ❌ Not all summaries generated after {max_wait}s")
    return False

def test_book_listing():
    """Test listing books with summaries"""
    print("\n" + "="*70)
    print("🧪 TEST: Book Listing with Summaries")
    print("="*70)
    
    username = random_username()
    
    # Register and upload
    print(f"\n1️⃣  Setting up test data...")
    resp = requests.post(f"{BASE_URL}/auth/register", json={
        "username": username,
        "email": f"{username}@test.com",
        "password": "testpass123",
        "full_name": "Test User"
    })
    token = resp.json()["access_token"]
    
    files = {
        'file': ('test.txt', 'This is a test book. It has content. The content is meant to be summarized by our system.', 'text/plain')
    }
    data = {
        'title': 'Test Book',
        'author': 'Test Author'
    }
    headers = {'Authorization': f'Bearer {token}'}
    
    resp = requests.post(f"{BASE_URL}/books/", files=files, data=data, headers=headers)
    book_id = resp.json()['id']
    print(f"   ✅ Book uploaded")
    
    # Wait for summary
    print(f"\n2️⃣  Waiting for summary...")
    for i in range(0, 30, 2):
        resp = requests.get(f"{BASE_URL}/books/", headers=headers)
        books_list = resp.json()['books']
        for book in books_list:
            if book.get('metadata', {}).get('summary'):
                print(f"   ✅ Summary found!")
                print(f"   📊 Books in list: {len(books_list)}")
                print(f"   📖 Book with summary: {book['title']}")
                return True
        time.sleep(2)
    
    print(f"   ❌ Summary not found")
    return False

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🚀 BOOK SUMMARIZATION - COMPREHENSIVE TEST SUITE")
    print("="*70)
    
    results = []
    
    try:
        results.append(("Single Book", test_single_book()))
    except Exception as e:
        print(f"\n❌ Single book test failed: {e}")
        results.append(("Single Book", False))
    
    try:
        results.append(("Multiple Books", test_multiple_books()))
    except Exception as e:
        print(f"\n❌ Multiple books test failed: {e}")
        results.append(("Multiple Books", False))
    
    try:
        results.append(("Book Listing", test_book_listing()))
    except Exception as e:
        print(f"\n❌ Book listing test failed: {e}")
        results.append(("Book Listing", False))
    
    # Summary
    print("\n" + "="*70)
    print("📊 TEST RESULTS SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Book summarization is fully functional.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check logs for details.")
