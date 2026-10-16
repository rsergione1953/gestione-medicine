package it.spsoft.gestionemedicine;

import android.app.NotificationManager;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;

public class MedicineAcknowledgeReceiver extends BroadcastReceiver {
    public static final String ACTION_ACKNOWLEDGE =
            "it.spsoft.gestionemedicine.ACKNOWLEDGE_LOW_STOCK";
    public static final String EXTRA_NOTIFICATION_ID = "notification_id";

    @Override
    public void onReceive(Context context, Intent intent) {
        if (!ACTION_ACKNOWLEDGE.equals(intent.getAction())) return;
        int notificationId = intent.getIntExtra(EXTRA_NOTIFICATION_ID, 0);
        if (notificationId == 0) return;
        NotificationManager manager =
                (NotificationManager) context.getSystemService(Context.NOTIFICATION_SERVICE);
        if (manager != null) manager.cancel(notificationId);
    }
}
