using KRPC.Service.Attributes;
using KRPC.SpaceCenter.ExtensionMethods;
using KRPC.Utils;
using UnityEngine;
using Tuple3 = KRPC.Utils.Tuple<double, double, double>;

namespace KRPC.SpaceCenter.Services.Parts
{
    /// <summary>
    /// Obtained by calling <see cref="Part.AddForce"/>.
    /// </summary>
    [KRPCClass (Service = "SpaceCenter")]
    public sealed class Force
    {
        readonly Rigidbody rigidBody;
        Vector3 force;
        Vector3 position;

        internal Force (Part part, Tuple3 forceVector, Tuple3 forcePosition, ReferenceFrame referenceFrame)
        {
            Part = part;
            rigidBody = part.InternalPart.GetComponent<Rigidbody> ();
            force = forceVector.ToVector ();
            position = forcePosition.ToVector ();
            ReferenceFrame = referenceFrame;
        }

        /// <summary>
        /// The part that this force is applied to.
        /// </summary>
        [KRPCProperty]
        public Part Part { get; private set; }

        /// <summary>
        /// The force vector. The magnitude of the vector is the strength of the force in Newtons.
        /// </summary>
        [KRPCProperty]
        public Tuple3 ForceVector {
            get { return force.ToTuple (); }
            set { force = value.ToVector (); }
        }

        /// <summary>
        /// The position at which the force acts.
        /// </summary>
        [KRPCProperty]
        public Tuple3 Position {
            get { return position.ToTuple (); }
            set { position = value.ToVector (); }
        }

        /// <summary>
        /// The reference frame of the force vector and position.
        /// </summary>
        [KRPCProperty]
        public ReferenceFrame ReferenceFrame { get; set; }

        /// <summary>
        /// Remove the force.
        /// </summary>
        [KRPCMethod]
        public void Remove ()
        {
            PartForcesAddon.Remove (this);
            //TODO: delete the object
        }

        internal void Update ()
        {
            var worldForce = ReferenceFrame.DirectionToWorldSpace (force);
            var worldPosition = ReferenceFrame.PositionToWorldSpace (position);
            rigidBody.AddForceAtPosition (worldForce, worldPosition, ForceMode.Force);
        }
    }
}