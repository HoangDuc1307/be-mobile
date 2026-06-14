from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from rooms.models import RoomTenant

User = get_user_model()


class Command(BaseCommand):
    help = 'Deactivate duplicate active RoomTenant records, keeping only the latest per tenant and per room'

    def handle(self, *args, **options):
        fixed_tenant = 0
        fixed_room = 0

        # Fix: 1 user has multiple active rooms → keep only the latest
        for user in User.objects.all():
            active_rts = RoomTenant.objects.filter(tenant=user, is_active=True).order_by('-id')
            if active_rts.count() > 1:
                keep = active_rts.first()
                duplicates = active_rts.exclude(id=keep.id)
                self.stdout.write(
                    f'User {user.username}: keeping room {keep.room.name}, '
                    f'deactivating {duplicates.count()} duplicate(s)'
                )
                for rt in duplicates:
                    # Also reset the room status if it was incorrectly set to occupied
                    rt.is_active = False
                    rt.save()
                fixed_tenant += duplicates.count()

        # Fix: 1 room has multiple active tenants → keep only the latest
        from rooms.models import Room
        for room in Room.objects.all():
            active_rts = RoomTenant.objects.filter(room=room, is_active=True).order_by('-id')
            if active_rts.count() > 1:
                keep = active_rts.first()
                duplicates = active_rts.exclude(id=keep.id)
                self.stdout.write(
                    f'Room {room.name}: keeping tenant {keep.tenant.username}, '
                    f'deactivating {duplicates.count()} duplicate(s)'
                )
                duplicates.update(is_active=False)
                fixed_room += duplicates.count()

        # Sync room statuses based on active RoomTenant
        for room in Room.objects.all():
            has_active = RoomTenant.objects.filter(room=room, is_active=True).exists()
            correct_status = 'occupied' if has_active else 'available'
            if room.status != correct_status:
                self.stdout.write(f'Room {room.name}: fixing status {room.status} -> {correct_status}')
                room.status = correct_status
                room.save()

        self.stdout.write(self.style.SUCCESS(
            f'Done. Fixed {fixed_tenant} duplicate tenant records, {fixed_room} duplicate room records.'
        ))
