from app import db, MenuItem, app

# This is the central location for ALL hotel menu data.
# To add a new hotel, just add a new entry to this dictionary.
MENU_DATA = {
    'lazar': [
        {'name': 'Chicken Biriyani', 'price': 180.0, 'image': 'chicken1.jpeg'},
        {'name': 'Egg Biriyani', 'price': 190.0, 'image': 'egg1.jpeg'},
        {'name': 'Mutton Biriyani', 'price': 260.0, 'image': 'mutton1.jpeg'},
        {'name': 'Veg Meals', 'price': 90.0, 'image': 'meals1.jpeg'},
        {'name': 'Curd Rice', 'price': 50.0, 'image': 'Curd rice1.jpeg'},
        {'name': 'Fish Biriyani', 'price': 150.0, 'image': 'Fish1.jpeg'},
    ],
    'nani': [
        {'name': 'Chicken Biriyani', 'price': 180.0, 'image': 'chicken1.jpeg'},
        {'name': 'Egg Biriyani', 'price': 190.0, 'image': 'egg1.jpeg'},
        {'name': 'Mutton Biriyani', 'price': 260.0, 'image': 'mutton1.jpeg'},
        {'name': 'Veg Meals', 'price': 90.0, 'image': 'meals1.jpeg'},
        {'name': 'Curd Rice', 'price': 50.0, 'image': 'Curd rice1.jpeg'},
        {'name': 'Fish Biriyani', 'price': 150.0, 'image': 'Fish1.jpeg'},
    ],
    'mariyamma': [
        {'name': 'Veg Biriyani', 'price': 100.0, 'image': 'Veg Biriyani.jpeg'},
        {'name': 'Egg Biriyani', 'price': 90.0, 'image': 'egg2.jpeg'},
        {'name': 'Mutton Biriyani', 'price': 160.0, 'image': 'mutton2.jpeg'},
        {'name': 'France Biryani', 'price': 260.0, 'image': 'france2.jpeg'},
        {'name': 'Veg Meals', 'price': 70.0, 'image': 'meals2.jpeg'},
        {'name': 'Curd Rice', 'price': 80.0, 'image': 'curd rice.jpeg'},
    ],
    'bhasker': [
        {'name': 'Chicken Biriyani', 'price': 100.0, 'image': 'chicken3.jpeg'},
        {'name': 'Egg Biriyani', 'price': 90.0, 'image': 'egg3.jpeg'},
        {'name': 'Mutton Biriyani', 'price': 160.0, 'image': 'mutton3.jpeg'},
        {'name': 'Veg Meals', 'price': 70.0, 'image': 'meals3.jpeg'},
        {'name': 'France Biryani', 'price': 80.0, 'image': 'france1.jpeg'},
        {'name': 'Fish Biryani', 'price': 60.0, 'image': 'fish1.jpeg'},
        {'name': 'Fish Fry', 'price': 100.0, 'image': 'fish2.jpeg'},
        {'name': 'Chicken Fry', 'price': 100.0, 'image': 'chicken fry.jpeg'},
    ]
}

def populate_database():
    """
    Populates the database with menu items for all hotels,
    avoiding duplicate entries.
    """
    with app.app_context():
        # Ensure all tables are created before populating.
        db.create_all()
        print("Database tables checked/created.")

        any_item_added = False
        for hotel_name, items in MENU_DATA.items():
            # Check if the hotel already has items to prevent duplication.
            if MenuItem.query.filter_by(hotel=hotel_name).count() == 0:
                print(f"Adding menu items for '{hotel_name}' hotel...")
                for item_data in items:
                    menu_item = MenuItem(
                        name=item_data['name'],
                        price=item_data['price'],
                        image=item_data.get('image'),
                        hotel=hotel_name
                    )
                    db.session.add(menu_item)
                any_item_added = True
            else:
                print(f"Menu items for '{hotel_name}' hotel already exist.")
        
        if any_item_added:
            db.session.commit()
            print("New items have been committed to the database.")
        else:
            print("No new items were added.")

if __name__ == '__main__':
    populate_database()