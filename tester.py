from model_classes import Person, Address, Phone

def main():
    print("=" * 50)
    print("TESTING PERSON CLASS")
    print("=" * 50)
    
    # Test 1: Basic creation and string representation
    print("\n1. Testing basic creation and __str__:")
    person1 = Person("P001", "John Doe", 30, True)
    person2 = Person("P002", "Jane Smith", 25, False)
    print(f"Person 1: {person1}")
    print(f"Person 2: {person2}")
    
    # Test 2: Equality testing
    print("\n2. Testing equality (__eq__):")
    person3 = Person("P001", "John Different", 35, True)  # Same ID, different other fields
    print(f"person1 == person3 (same ID): {person1 == person3}")
    print(f"person1 == person2 (different ID): {person1 == person2}")

if __name__ == "__main__":
    main()