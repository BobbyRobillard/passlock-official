from passwords.models import Password, Subscriber

from cryptography.fernet import Fernet


def setup_demo_password(form):
    s = Subscriber.objects.create(user=form.instance)

    file = open('key.key', 'rb')
    key = file.read()
    file.close()

    demo_password_name = "Demo Password".encode()
    demo_username = "Demo Username".encode()
    demo_password = "DemoPassword123!".encode()

    fernet = Fernet(key)
    demo_password_name = fernet.encrypt(demo_password_name)
    demo_username = fernet.encrypt(demo_username)
    demo_password = fernet.encrypt(demo_password)

    Password.objects.create(
        subscriber=s,
        name=demo_password_name,
        username=demo_username,
        hashed_password=demo_password,
        challenge_time=1,
    )
